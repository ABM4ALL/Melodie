import argparse
import base64
import importlib
import json
import sys
import time
import rpyc
from typing import Dict, Tuple, Any, Type, Union, TYPE_CHECKING

import cloudpickle

from MelodieInfra.config.global_configs import MelodieGlobalConfig

if TYPE_CHECKING:
    from Melodie import Calibrator, Trainer, Scenario, Model, Simulator

parser = argparse.ArgumentParser()
parser.add_argument("--core_id", help="ID of core")
parser.add_argument("--workdirs", help="Working directories")
parser.add_argument("--role", help="Roles,`calibrator` or `trainer`")
args = parser.parse_args()

workdirs = json.loads(args.workdirs)
sys.path = workdirs + sys.path


class ParallelWorker:
    def __init__(self):
        self.role = args.role
        assert self.role in {"trainer", "calibrator", "simulator"}
        self.core_id = args.core_id
        self.conn = rpyc.connect(
            "localhost", 12233, keepalive=True, config={"sync_request_timeout": None}
        )

    def get_config(self):
        return json.loads(self.conn.root.get_config())

    def get_task(self):
        while 1:
            # try:
            task_raw = self.conn.root.get_task()
            # except rpyc.AsyncResultTimeout:
            #     continue
            task = cloudpickle.loads(base64.b64decode(task_raw))
            if task is None:
                time.sleep(0.1)
            else:
                return tuple(task)

    def put_result(self, result):
        return self.conn.root.put_result(result)

    def close(self):
        self.conn.close()

    def run(self):
        config = self.get_config()
        if self.role == "calibrator":
            sub_routine_calibrator(self.core_id, config[0], config[1], self)
        elif self.role == "trainer":
            sub_routine_trainer(self.core_id, config[0], config[1], self)
        elif self.role == "simulator":
            sub_routine_simulator(self.core_id, config[0], config[1], self)
        else:
            raise NotImplementedError(f"Unrecognized role `{self.role}`")


def get_scenario_manager(
    config, modules: Dict
) -> Tuple[Union["Trainer", "Calibrator"], Type["Scenario"], Type["Model"]]:
    from Melodie import Trainer, Calibrator

    classes_dict = {}
    for module_type, content in modules.items():
        if content is not None:
            class_name, module_name = content
            module = importlib.import_module(module_name)
            cls = getattr(module, class_name)
            classes_dict[module_type] = cls
        else:
            classes_dict[module_type] = None

    trainer: "Union[Trainer, Calibrator, Simulator]" = classes_dict["trainer"](
        config=config,
        scenario_cls=classes_dict["scenario"],
        model_cls=classes_dict["model"],
        data_loader_cls=classes_dict["data_loader"],
    )
    trainer.setup()
    if isinstance(trainer, (Trainer, Calibrator)):
        trainer.collect_data()
    trainer.subworker_prerun()
    return trainer, classes_dict["scenario"], classes_dict["model"]


def sub_routine_trainer(
    proc_id: int,
    modules: Dict[str, Tuple[str, str]],
    config_raw: Dict[str, Any],
    worker: ParallelWorker,
):
    """
    The sub iterator callback for parallelized computing used in Trainer and Calibrator.

    :param proc_id:
    :param modules:
    :param config_raw:
    :return:
    """
    from Melodie import Config, Trainer, Environment, AgentList, Agent
    import logging

    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    logger = logging.getLogger(f"Trainer-processor-{proc_id}")
    logger.info("subroutine started!")
    try:
        config = Config.from_dict(config_raw)
        trainer: Trainer
        trainer, scenario_cls, model_cls = get_scenario_manager(config, modules)
    except BaseException:
        import traceback

        traceback.print_exc()
        return

    while 1:
        try:
            t0 = time.time()

            chrom, d, agent_params = worker.get_task()
            logger.debug(f"processor {proc_id} got chrom {chrom}")
            scenario = scenario_cls()
            scenario._setup()
            scenario.set_params(d)
            model = model_cls(config, scenario)
            scenario.manager = trainer
            model.create()
            model._setup()
            # {category: [{id: 0, param1: 1, param2: 2, ...}]}
            for category, params in agent_params.items():
                agent_container: AgentList[Agent] = getattr(model, category)
                for param in params:
                    agent = agent_container.get_agent(param["id"])
                    agent.set_params(param)
            model.run()
            agent_data = {}
            for container in trainer.container_manager.agent_containers:
                agent_container = getattr(model, container.container_name)
                df = agent_container.to_list(container.recorded_properties)
                agent_data[container.container_name] = df
                for row in df:
                    agent = agent_container.get_agent(row["id"])
                    row["target_function_value"] = trainer.target_function(agent)
                    row["utility"] = trainer.utility(agent)
                    row["agent_id"] = row.pop("id")
            env: Environment = model.environment
            env_data = env.to_dict(trainer.environment_properties)
            dumped = cloudpickle.dumps((chrom, agent_data, env_data))
            t1 = time.time()
            logger.info(
                f"Processor {proc_id}, chromosome {chrom}, time: {MelodieGlobalConfig.Logger.round_elapsed_time(t1 - t0)}s"
            )
            worker.put_result(base64.b64encode(dumped))
        except Exception:
            import traceback

            traceback.print_exc()


def sub_routine_calibrator(
    proc_id: int,
    modules: Dict[str, Tuple[str, str]],
    config_raw: Dict[str, Any],
    worker: ParallelWorker,
):
    """
    The sub iterator callback for parallelized computing used in Trainer and Calibrator.

    :param proc_id:
    :param modules:
    :param config_raw:
    :return:
    """
    from Melodie import Config, Environment
    import logging

    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    logger = logging.getLogger(f"Calibrator-processor-{proc_id}")
    logger.info("subroutine started!")
    try:
        config = Config.from_dict(config_raw)
        calibrator: "Calibrator"
        calibrator, scenario_cls, model_cls = get_scenario_manager(config, modules)
    except BaseException:
        import traceback

        traceback.print_exc()
        return
    while 1:
        try:
            ret = worker.get_task()
            t0 = time.time()
            chrom, d, env_params = ret
            logger.debug(f"processor {proc_id} got chrom {chrom}")
            scenario: Scenario = scenario_cls()
            scenario.manager = calibrator
            scenario._setup()
            scenario.set_params(d)
            scenario.set_params(env_params)
            model = model_cls(config, scenario)
            model.create()
            model._setup()
            model.run()
            agent_data = {}
            for container_name, props in calibrator.recorded_agent_properties.items():
                agent_container = getattr(model, container_name)
                df = agent_container.to_list(props)
                agent_data[container_name] = df
                for row in df:
                    row["agent_id"] = row.pop("id")
            env: Environment = model.environment
            env_data = env.to_dict(calibrator.watched_env_properties)
            env_data.update(
                {prop: scenario.to_dict()[prop] for prop in calibrator.properties}
            )
            env_data["target_function_value"] = env_data[
                "distance"
            ] = calibrator.distance(model)
            dumped = cloudpickle.dumps((chrom, agent_data, env_data))
            t1 = time.time()
            logger.info(
                f"Processor {proc_id}, chromosome {chrom}, time: {MelodieGlobalConfig.Logger.round_elapsed_time(t1 - t0)}s"
            )
            worker.put_result(base64.b64encode(dumped))
        except Exception:
            import traceback

            traceback.print_exc()


def sub_routine_simulator(
    proc_id: int,
    modules: Dict[str, Tuple[str, str]],
    config_raw: Dict[str, Any],
    worker: ParallelWorker,
):
    """
    The sub iterator callback for parallelized computing used for Simulator.

    :param proc_id:
    :param modules:
    :param config_raw:
    :return:
    """
    from Melodie import Config, Environment
    import logging

    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    logger = logging.getLogger(f"Simulator-processor-{proc_id}")
    logger.info("subroutine started!")
    try:
        config = Config.from_dict(config_raw)
        simulator: "Simulator"
        simulator, scenario_cls, model_cls = get_scenario_manager(config, modules)
    except BaseException:
        import traceback

        traceback.print_exc()
        dumped = cloudpickle.dumps(0)
        worker.put_result(base64.b64encode(dumped))
        return
    while 1:
        try:
            ret = worker.get_task()
            t0 = time.time()
            id_run, d, env_params = ret
            logger.debug(f"processor {proc_id} got id_run {id_run}")
            scenario: Scenario = scenario_cls()
            scenario.manager = simulator
            scenario._setup()
            scenario.set_params(d, asserts_key_exist=False)
            # scenario.set_params(env_params)
            model = model_cls(config, scenario, run_id_in_scenario=id_run)

            model.create()
            model._setup()
            model.run()

            dumped = cloudpickle.dumps((id_run, None, None))
            t1 = time.time()
            logger.info(
                f"Processor {proc_id}, run {id_run}, time: {MelodieGlobalConfig.Logger.round_elapsed_time(t1 - t0)}s"
            )
            worker.put_result(base64.b64encode(dumped))
        except Exception:
            import traceback

            traceback.print_exc()
            dumped = cloudpickle.dumps((None, None, None))
            logger.info(f"Processor {proc_id} failed")
            worker.put_result(base64.b64encode(dumped))


if __name__ == "__main__":
    worker = ParallelWorker()
    worker.run()
