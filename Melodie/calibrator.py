import copy
import logging
import time
from typing import (
    Dict,
    Tuple,
    Callable,
    Union,
    List,
    Any,
    Optional,
    TYPE_CHECKING,
    Type,
    Iterator,
    cast,
)

import pandas as pd

from MelodieInfra import create_db_conn, Config, MelodieExceptions

from .algorithms import AlgorithmParameters
from .algorithms.ga import MelodieGA
from .data_loader import DataLoader
from .model import Model
from .scenario_manager import Scenario
from .simulator import BaseModellingManager
from .utils.parallel_manager import ParallelManager

if TYPE_CHECKING:
    from .boost.basics import Environment
logger = logging.getLogger(__name__)

pool = None  # on *nix
th_on_thread = None  # for windows


class GACalibratorParams(AlgorithmParameters):
    def __init__(
            self,
            id: int,
            path_num: int,
            generation_num: int,
            strategy_population: int,
            mutation_prob: int,
            strategy_param_code_length: int,
            **kw,
    ):
        super().__init__(id, path_num)

        self.generation_num = generation_num
        self.strategy_population = strategy_population
        self.mutation_prob = mutation_prob
        self.strategy_param_code_length = strategy_param_code_length
        self.parse_params(kw)

    @staticmethod
    def from_dataframe_record(
            record: Dict[str, Union[int, float]]
    ) -> "GACalibratorParams":
        s = GACalibratorParams(
            record["id"],
            record["path_num"],
            record["generation_num"],
            record["strategy_population"],
            record["mutation_prob"],
            record["strategy_param_code_length"],
        )
        s.parse_params(record)
        return s

    def __hash__(self):
        return hash(
            (
                self.id,
                self.path_num,
                self.generation_num,
                self.strategy_population,
                self.mutation_prob,
                self.strategy_param_code_length,
            )
        )


class CalibratorAlgorithmMeta:
    """
    Record the current scenario, params scenario, path and generation
    of trainer.

    """

    def __init__(self):
        self._freeze = False
        self.id_calibrator_scenario = 0
        self.id_calibrator_params_scenario = 1
        self.id_path = 0
        self.id_generation = 0

    def to_dict(self, public_only=False):

        if public_only:
            return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}
        return copy.copy(self.__dict__)

    def __repr__(self):
        return f"<{self.to_dict()}>"

    def __setattr__(self, key, value):
        if (not hasattr(self, "_freeze")) or (not self._freeze):
            super().__setattr__(key, value)
        else:
            if key in self.__dict__:
                super().__setattr__(key, value)
            else:
                raise MelodieExceptions.General.NoAttributeError(self, key)


class GACalibratorAlgorithmMeta(CalibratorAlgorithmMeta):
    def __init__(self):
        super(GACalibratorAlgorithmMeta, self).__init__()
        self.id_chromosome = 0
        self._freeze = True


class GACalibratorAlgorithm:
    """
    参数：一个tuple
    每次会跑20条染色体，然后将参数缓存起来。
    目标函数从TargetFcnCache中查询。
    """

    def __init__(
            self,
            env_param_names: List[str],
            recorded_env_properties: List[str],
            recorded_agent_properties: Dict[str, List[str]],
            params: GACalibratorParams,
            target_func: "Callable[[Model], Union[float, int]]",
            manager: "Calibrator" = None,
            processors=1,
    ):
        global pool, th_on_thread
        self.manager = manager
        self.params = params
        self.chromosomes = 20
        self.target_func = target_func
        self.env_param_names = env_param_names
        self.recorded_env_properties = recorded_env_properties
        self.recorded_agent_properties = recorded_agent_properties
        lb, ub = self.params.bounds(self.env_param_names)
        self.algorithm: Optional[MelodieGA] = MelodieGA(
            cast("function", self.generate_target_function()),
            len(self.env_param_names),
            self.params.strategy_population,
            self.params.generation_num,
            self.params.mutation_prob,
            lb,
            ub,
            precision=1e-5,
        )
        self.cache: Dict[Tuple[int, int], float] = {}
        # self.agent_container_getters: Dict[str, Callable[[Model], AgentList]] = {}
        # self.agent_ids: Dict[str, List[int]] = {}  # {category : [agent_id]}
        # self.agent_params_defined: Dict[str, List[str]] = {}  # category: [param_name1, param_name2...]
        # self.recorded_agent_properties: Dict[str, List[str]] = {}  # category: [prop1, prop2...]
        # self.recorded_env_properties: List[str] = []  # category: [prop1, prop2...]

        self._chromosome_counter = 0
        self._current_generation = 0
        self.processors = processors
        d = {
            "model": (
                self.manager.model_cls.__name__,
                self.manager.model_cls.__module__,
            ),
            "scenario": (
                self.manager.scenario_cls.__name__,
                self.manager.scenario_cls.__module__,
            ),
            "trainer": (
                self.manager.__class__.__name__,
                self.manager.__class__.__module__,
            ),
            "data_loader": (
                self.manager.df_loader_cls.__name__,
                self.manager.df_loader_cls.__module__,
            ),
        }

        self.parallel_manager = ParallelManager(
            self.processors, configs=(d, self.manager.config.to_dict())
        )
        self.parallel_manager.run("calibrator")

    def stop(self):
        self.parallel_manager.close()

    def get_params(self, id_chromosome: int) -> Dict[str, Any]:
        """
        Pass parameters from the chromosome to the Environment.

        :param id_chromosome:
        :return:
        """
        chromosome_value = self.algorithm.chrom2x(self.algorithm.Chrom)[id_chromosome]
        env_parameters_dict = {}
        for i, param_name in enumerate(self.env_param_names):
            env_parameters_dict[param_name] = chromosome_value[i]
        return env_parameters_dict

    def target_function_to_cache(
            self,
            env_data,
            generation: int,
            id_chromosome: int,
    ):
        """
        Extract the value of target functions from Model, and write them into cache.

        :return:
        """
        self.cache[(generation, id_chromosome)] = env_data["target_function_value"]

    def generate_target_function(self) -> Callable[[], float]:
        """
        Generate the target function.

        :return:
        """

        def f(*args):
            self._chromosome_counter += 1
            value = self.cache[(self._current_generation, self._chromosome_counter)]
            return value

        return f

    def record_agent_properties(
            self,
            agent_data: Dict[str, List[Dict[str, Any]]],
            env_data: Dict[str, Any],
            meta: GACalibratorAlgorithmMeta,
    ):
        """
        Record the property of each agent in the current chromosome.

        :param agent_data: {<agent_container_name>: [{id: 0, prop1: xxx, prop2: xxx, ...}]}
        :param env_data: {env_prop1: xxx, env_prop2: yyy, ...}
        :param meta:
        :return:
        """
        agent_records = {}
        environment_record = {}
        meta_dict = meta.to_dict(public_only=True)

        for container_name, _ in self.recorded_agent_properties.items():
            agent_records[container_name] = []
            data = agent_data[container_name]
            for agent_container_data in data:
                d = {}
                d.update(meta_dict)
                d.update(agent_container_data)

                agent_records[container_name].append(d)
            create_db_conn(self.manager.config).write_dataframe(
                f"{container_name}_calibrator_result",
                pd.DataFrame(agent_records[container_name]),
                if_exists="append",
            )
        environment_record.update(meta_dict)
        environment_record.update(env_data)
        environment_record.pop("target_function_value")

        create_db_conn(self.manager.config).write_dataframe(
            "environment_calibrator_result",
            pd.DataFrame([environment_record]),
            if_exists="append",
        )
        return agent_records, environment_record

    def calc_cov_df(
            self,
            agent_container_df_dict: Dict[str, pd.DataFrame],
            env_df: pd.DataFrame,
            meta,
    ):
        """
        Calculate the coefficient of variation
        :param agent_container_df_dict:
        :param env_df:
        :param meta:
        :return:
        """

        pd.set_option("max_colwidth", 500)
        pd.set_option("display.max_columns", None)
        pd.set_option("display.max_rows", None)
        meta_dict = meta.to_dict(public_only=True)
        meta_dict.pop("id_chromosome")
        for container_name in self.recorded_agent_properties.keys():
            df = agent_container_df_dict[container_name]
            container_agent_record_list = []
            for agent_id in self.recorded_agent_properties[container_name]:
                agent_data = df.loc[df["agent_id"] == agent_id]
                cov_records = {}
                cov_records.update(meta_dict)
                cov_records["agent_id"] = agent_id
                for prop_name in self.recorded_agent_properties[container_name] + [
                    "distance"
                ]:
                    p: pd.Series = agent_data[prop_name]
                    mean = p.mean()
                    cov = p.std() / p.mean()
                    cov_records.update(
                        {prop_name + "_mean": mean, prop_name + "_cov": cov}
                    )
                container_agent_record_list.append(cov_records)
            create_db_conn(self.manager.config).write_dataframe(
                f"{container_name}_calibrator_result_cov",
                pd.DataFrame(container_agent_record_list),
                if_exists="append",
            )
        env_record = {}
        env_record.update(meta_dict)
        for prop_name in (
                self.env_param_names + self.recorded_env_properties + ["distance"]
        ):
            mean = env_df[prop_name].mean()
            cov = env_df[prop_name].std() / env_df[prop_name].mean()
            env_record.update({prop_name + "_mean": mean, prop_name + "_cov": cov})
        create_db_conn(self.manager.config).write_dataframe(
            "environment_calibrator_result_cov",
            pd.DataFrame([env_record]),
            if_exists="append",
        )

    def pre_check(self, meta):
        """
        Check at the beginning of run()
        :return:
        """
        logger.info(f"""Algorithm will run with:
        Meta value: {meta}
        Recording environment parameters: {self.recorded_env_properties}
        Recording Agent agent_lists: {self.recorded_agent_properties}\n""")

    def run(self, scenario: Scenario, meta: Union[GACalibratorAlgorithmMeta]):
        self.pre_check(meta)

        for i in range(self.params.generation_num):
            t0 = time.time()
            self._current_generation = i
            meta.id_generation = i
            logger.info(
                f"======================="
                f"Path {meta.id_path} Generation {i + 1}/{self.params.generation_num}"
                f"======================="
            )

            for id_chromosome in range(self.params.strategy_population):
                params = self.get_params(id_chromosome)
                # params_queue.put(
                #     json.dumps((id_chromosome, scenario.to_json(), params))
                # )
                self.parallel_manager.put_task(
                    (id_chromosome, scenario.to_json(), params)
                )

            agent_records_collector: Dict[str, List[Dict[str, Any]]] = {
                container_name: []
                for container_name in self.recorded_agent_properties.keys()
            }
            env_records_list: List[Dict[str, Any]] = []

            for _id_chromosome in range(self.params.strategy_population):
                chrom, agents_data, env_data = self.parallel_manager.get_result()
                meta.id_chromosome = chrom
                agent_records, env_record = self.record_agent_properties(
                    agents_data, env_data, meta
                )
                for container_name, records in agent_records.items():
                    agent_records_collector[container_name] += records
                env_records_list.append(env_record)
                self.target_function_to_cache(env_data, i, chrom)

            self.calc_cov_df(
                {k: pd.DataFrame(v) for k, v in agent_records_collector.items()},
                pd.DataFrame(env_records_list),
                meta,
            )

            self._chromosome_counter = -1
            self.algorithm.run(1)
            t1 = time.time()
            logger.info("=" * 20 + f"Time Elapsed: {t1 - t0}s" + "=" * 20)


class Calibrator(BaseModellingManager):
    def __init__(
            self,
            config: "Config",
            scenario_cls: "Optional[Type[Scenario]]",
            model_cls: "Optional[Type[Model]]",
            data_loader_cls: Type["DataLoader"],
            processors=1,
    ):
        super().__init__(
            config=config,
            scenario_cls=scenario_cls,
            model_cls=model_cls,
            data_loader_cls=data_loader_cls,
        )
        self.processes = processors
        self.training_strategy: "Optional[Type[SearchingAlgorithm]]" = None
        self.container_name: str = ""

        self.properties: List[str] = []
        self.watched_env_properties: List[str] = []
        self.recorded_agent_properties: Dict[str, List[str]] = {}
        self.algorithm: Optional[GACalibratorAlgorithm] = None
        self.algorithm_instance: Iterator[List[float]] = {}

        self.model: Optional[Model] = None

        self.current_algorithm_meta = GACalibratorAlgorithmMeta()
        self.df_loader_cls = data_loader_cls

    def setup(self):
        """
        Setup method, be sure to inherit this method in custom calibrator class.
        """
        pass

    def collect_data(self):
        """
        Set the agent and environment properties to be collected.

        """
        pass

    def generate_scenarios(self) -> List["Scenario"]:
        """
        Generate scenario objects by the parameter from static tables or scenarios_dataframe.
        
        :return: A list of generated scenarios.
        """
        return self.data_loader.generate_scenarios_from_dataframe(
            "calibrator_scenarios"
        )

    def get_params_scenarios(self) -> List:
        """
        Get the parameters of calibrator parameters from the registered dataframe.

        :return: A list of dict, and each dict contains parameters.
        """
        calibrator_scenarios_table = self.get_dataframe("calibrator_params_scenarios")
        assert isinstance(
            calibrator_scenarios_table, pd.DataFrame
        ), "No learning scenarios table specified!"
        return calibrator_scenarios_table.to_dict(orient="records")

    def run(self):
        """
        The main method for calibrator.

        """
        self.setup()
        self.pre_run()

        scenario_cls = GACalibratorParams
        for scenario in self.scenarios:
            self.current_algorithm_meta.id_calibrator_scenario = scenario.id
            calibration_scenarios = self.get_params_scenarios()
            for calibrator_scenario in calibration_scenarios:
                calibrator_scenario = scenario_cls.from_dataframe_record(
                    calibrator_scenario
                )
                self.current_algorithm_meta.id_calibrator_params_scenario = (
                    calibrator_scenario.id
                )
                for id_trainer_path in range(calibrator_scenario.path_num):
                    self.current_algorithm_meta.id_path = id_trainer_path

                    self.run_once_new(scenario, calibrator_scenario)

    def run_once_new(self, scenario: Scenario, calibration_params: GACalibratorParams):
        """
        Run for one calibration path

        :param scenario: The scenario to run.
        :param calibration_params: calibration parameters.
        :return: None
        """
        self.algorithm = GACalibratorAlgorithm(
            self.properties,
            self.watched_env_properties,
            {},
            calibration_params,
            self.target_function,
            manager=self,
            processors=self.processes,
        )
        self.algorithm.run(scenario, self.current_algorithm_meta)
        self.algorithm.stop()

    def target_function(self, model: "Model") -> Union[float, int]:
        """
        The target function to be minimized

        :param env: Environment of the current model.
        :return:
        """
        return self.distance(model)

    def distance(self, model: "Model") -> float:
        """
        The optimization of calibrator is to minimize the distance.

        Be sure to inherit this function in custom calibrator, and return a float value.

        :param model: The current model after running the current parameter set.
        :return: None
        """
        raise NotImplementedError(
            "Calibrator.distance(model) must be overridden in sub-class!"
        )

    def add_scenario_calibrating_property(self, prop: str):
        """
        Add a property to be tuned in the calibration, and ``prop`` should be a name of property in the environment.

        :param prop: Property name
        :return: None
        """
        assert (
                prop not in self.properties
        ), f'Property "{prop}" is already in the calibrating training_properties!'
        self.properties.append(prop)

    def add_environment_property(self, prop: str):
        """
        Add a property of environment to be recorded in the calibration voyage.

        :param prop: Property name
        :return: None
        """
        assert prop not in self.watched_env_properties
        self.watched_env_properties.append(prop)
