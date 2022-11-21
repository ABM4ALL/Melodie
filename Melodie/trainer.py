import copy
import logging
from typing import (
    Dict,
    Tuple,
    Callable,
    Union,
    List,
    Any,
    Optional,
    Iterator,
    Type,
    cast,
)

import pandas as pd
from sko import GA

from MelodieInfra import Config, MelodieExceptions, create_db_conn

from .algorithms import AlgorithmParameters
from .algorithms.ga import MelodieGA
from .boost.agent_list import AgentList
from .boost.basics import Agent
from .data_loader import DataLoader
from .model import Model
from .scenario_manager import Scenario
from .simulator import BaseModellingManager
from .utils.parallel_manager import ParallelManager

logger = logging.getLogger(__name__)
pool = None  # for *nix
th_on_thread = None  # for windows


class GATrainerParams(AlgorithmParameters):
    def __init__(
            self,
            id: int,
            path_num: int,
            generation_num: int,
            strategy_population: int,
            mutation_prob: float,
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
    ) -> "GATrainerParams":
        s = GATrainerParams(
            record["id"],
            record["path_num"],
            record["generation_num"],
            record["strategy_population"],
            record["mutation_prob"],
            record["strategy_param_code_length"],
        )
        s.parse_params(record)
        return s

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.__dict__}>"

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


class TrainerAlgorithmMeta:
    """
    Record the current scenario, params scenario, path and generation
    of trainer.

    """

    def __init__(self):
        self._freeze = False
        self.trainer_id_scenario = 0
        self.trainer_params_id = 1
        self.path_id = 0
        self.generation = 0

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
                super(TrainerAlgorithmMeta, self).__setattr__(key, value)
            else:
                raise MelodieExceptions.General.NoAttributeError(self, key)


class GATrainerAlgorithmMeta(TrainerAlgorithmMeta):
    def __init__(self):
        super().__init__()
        self.chromosome_id = 0
        self._freeze = True


class TargetFcnCache:
    """
    The cache for the pre-computed values.

    Dict:  {(generation_id,
             chromosome_id):
                           {(agent_id,
                             container_name):
                                            function_value
                           }
          }
    """

    def __init__(self):
        self.target_fcn_record: Dict[Tuple[int, int], Dict] = {}
        self.current_generation = -1
        self.current_chromosome_id = -1

    def lookup_agent_target_value(
            self, agent_id: int, container_name: str, generation: int, chromosome_id: int
    ):
        return self.target_fcn_record[(generation, chromosome_id)][
            (agent_id, container_name)
        ]

    def set_agent_target_value(
            self,
            agent_id: int,
            container_name: str,
            value: float,
            generation: int,
            chromosome_id: int,
    ):
        # self.current_target_fcn_value[(agent_id, container_name)] = value
        if (generation, chromosome_id) not in self.target_fcn_record:
            self.target_fcn_record[(generation, chromosome_id)] = {}
        self.target_fcn_record[(generation, chromosome_id)][
            (agent_id, container_name)
        ] = value

    def best_value(
            self, chromosome_num: int, generation: int, agent_id: int, agent_category: int
    ):
        values = [
            self.target_fcn_record[(generation, chromosome_id)][
                (agent_id, agent_category)
            ]
            for chromosome_id in range(chromosome_num)
        ]
        return min(values)


class GATrainerAlgorithm:
    """
    参数：一个tuple
    每次会跑20条染色体，然后将参数缓存起来。
    目标函数从TargetFcnCache中查询。
    """

    def __init__(
            self, params: GATrainerParams, manager: "Trainer" = None, processors=1
    ):
        global pool, th_on_thread
        self.manager = manager
        self.params = params
        self.chromosomes = 20
        self.algorithms_dict: Dict[Tuple[int, str], Union[GA]] = {}

        self.target_fcn_cache = TargetFcnCache()
        self.agent_container_getters: Dict[str, Callable[[Model], AgentList]] = {}
        self.agent_ids: Dict[str, List[int]] = {}  # {category : [agent_id]}
        self.agent_params_defined: Dict[
            str, List[str]
        ] = {}  # category: [param_name1, param_name2...]
        self.recorded_agent_properties: Dict[
            str, List[str]
        ] = {}  # category: [prop1, prop2...]
        self.recorded_env_properties: List[str] = []  # category: [prop1, prop2...]

        self._chromosome_counter = 0
        self._current_generation = 0
        self.processors = processors

        # for i in range(processors):
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
        self.parallel_manager.run("trainer")

    def __del__(self):
        self.parallel_manager.close()

    def setup_agent_locations(
            self,
            container_name: str,
            param_names: List[str],
            recorded_properties: List[str],
            agent_id_list: List[int],
    ):
        assert container_name not in self.agent_container_getters
        self.agent_container_getters[container_name] = lambda model: getattr(
            model, container_name
        )
        lb, ub = self.params.bounds(param_names)
        for agent_id in agent_id_list:
            self.algorithms_dict[(agent_id, container_name)] = MelodieGA(
                func=cast(
                    "function", self.generate_target_function(agent_id, container_name)
                ),
                n_dim=len(param_names),
                size_pop=self.params.strategy_population,
                max_iter=self.params.generation_num,
                prob_mut=self.params.mutation_prob,
                lb=lb,
                ub=ub,
                precision=1e-5,
            )
        self.agent_params_defined[container_name] = param_names
        self.recorded_agent_properties[container_name] = recorded_properties
        self.agent_ids[container_name] = agent_id_list

    def get_agent_params(self, chromosome_id: int):
        """
        Pass parameters from the chromosome to the agent container.

        :param chromosome_id:
        :return:
        """
        params: Dict[str, List[Dict[str, Any]]] = {
            category: [] for category in self.agent_ids.keys()
        }
        # {category : [{id: 0, param1: 1, param2: 2, ...}]}
        for key, algorithm in self.algorithms_dict.items():
            chromosome_value = algorithm.chrom2x(algorithm.Chrom)[chromosome_id]
            agent_id, agent_category = key
            d = {"id": agent_id}
            for i, param_name in enumerate(self.agent_params_defined[agent_category]):
                d[param_name] = chromosome_value[i]
            params[agent_category].append(d)
        return params

    def target_function_to_cache(
            self,
            agent_target_function_values: Dict[str, List[Dict[str, Any]]],
            generation: int,
            chromosome_id: int,
    ):
        """
        Extract the value of target functions from Model, and write them into cache.

        :return:
        """
        for (
                container_category,
                container_getter,
        ) in self.agent_container_getters.items():
            agent_props_list = agent_target_function_values[container_category]
            for agent_props in agent_props_list:
                self.target_fcn_cache.set_agent_target_value(
                    agent_props["agent_id"],
                    container_category,
                    agent_props["target_function_value"],
                    generation,
                    chromosome_id,
                )

    def generate_target_function(
            self, agent_id: int, container_name: str
    ) -> Callable[[], float]:
        def f(*args):
            self._chromosome_counter += 1
            value = self.target_fcn_cache.lookup_agent_target_value(
                agent_id,
                container_name,
                self._current_generation,
                self._chromosome_counter,
            )
            return value

        return f

    def record_agent_properties(
            self,
            agent_data: Dict[str, List[Dict[str, Any]]],
            env_data: Dict[str, Any],
            meta: GATrainerAlgorithmMeta,
    ):
        """
        Record the property of each agent in the current chromosome.

        :param agent_data: {<agent_container_name>: [{id: 0, prop1: xxx, prop2: xxx, ...}]}
        :param env_data: {env_prop1: xxx, env_prop2: yyy, ...}
        :param meta:
        :return:
        """
        agent_records = {}
        env_record = {}
        meta_dict = meta.to_dict(public_only=True)

        for (
                container_name,
                agent_container_getter,
        ) in self.agent_container_getters.items():
            agent_records[container_name] = []
            data = agent_data[container_name]
            for agent_container_data in data:
                d = {}
                d.update(meta_dict)
                d["agent_id"] = agent_container_data["agent_id"]
                d.update(agent_container_data)
                d.pop("target_function_value")
                agent_records[container_name].append(d)
            create_db_conn(self.manager.config).write_dataframe(
                f"{container_name}_trainer_result",
                pd.DataFrame(agent_records[container_name]),
                if_exists="append",
            )
        env_record.update(meta_dict)
        env_record.update(env_data)

        create_db_conn(self.manager.config).write_dataframe(
            "env_trainer_result", pd.DataFrame([env_record]), if_exists="append"
        )

        return agent_records, env_record

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
        meta_dict.pop("chromosome_id")
        for container_name in self.agent_ids.keys():
            df = agent_container_df_dict[container_name]
            container_agent_record_list = []
            for agent_id in self.agent_ids[container_name]:
                agent_data = df.loc[df["agent_id"] == agent_id]
                cov_records = {}
                cov_records.update(meta_dict)
                cov_records["agent_id"] = agent_id
                for prop_name in self.recorded_agent_properties[container_name] + [
                    "utility"
                ]:
                    p: pd.Series = agent_data[prop_name]
                    mean = p.mean()
                    cov = p.std() / p.mean()
                    cov_records.update(
                        {prop_name + "_mean": mean, prop_name + "_cov": cov}
                    )
                container_agent_record_list.append(cov_records)
            create_db_conn(self.manager.config).write_dataframe(
                f"{container_name}_trainer_result_cov",
                pd.DataFrame(container_agent_record_list),
                if_exists="append",
            )
        env_record = {}
        env_record.update(meta_dict)
        for prop_name in self.recorded_env_properties:
            mean = env_df[prop_name].mean()
            cov = env_df[prop_name].std() / env_df[prop_name].mean()
            env_record.update({prop_name + "_mean": mean, prop_name + "_cov": cov})
        create_db_conn(self.manager.config).write_dataframe(
            "env_trainer_result_cov", pd.DataFrame([env_record]), if_exists="append"
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
        # print("Algorithm will run with:")
        # print("    Meta value", meta)
        # print("    Recording environment parameters: ", self.recorded_env_properties)
        # print("    Recording Agent agent_lists:", self.agent_container_getters)

    def run(self, scenario: Scenario, meta: Union[GATrainerAlgorithmMeta]):
        self.pre_check(meta)

        for i in range(self.params.generation_num):
            self._current_generation = i
            meta.generation = i
            logger.info(
                f"======================="
                f"Path {meta.path_id} Generation {i + 1}/{self.params.generation_num}"
                f"======================="
            )

            for chromosome_id in range(self.params.strategy_population):
                params = self.get_agent_params(chromosome_id)
                self.parallel_manager.put_task(
                    (chromosome_id, scenario.to_json(), params)
                )
                # params_queue.put(
                #     json.dumps()
                # )

            agent_records_collector: Dict[str, List[Dict[str, Any]]] = {
                container_name: [] for container_name in self.agent_ids.keys()
            }
            env_records_list: List[Dict[str, Any]] = []

            for _chromosome_id in range(self.params.strategy_population):
                # v = result_queue.get()

                (
                    chrom,
                    agents_data,
                    env_data,
                ) = (
                    self.parallel_manager.get_result()
                )  # cloudpickle.loads(base64.b64decode(v))
                meta.chromosome_id = chrom
                agent_records, env_record = self.record_agent_properties(
                    agents_data, env_data, meta
                )
                for container_name, records in agent_records.items():
                    agent_records_collector[container_name] += records
                env_records_list.append(env_record)
                self.target_function_to_cache(agents_data, i, chrom)

            self.calc_cov_df(
                {k: pd.DataFrame(v) for k, v in agent_records_collector.items()},
                pd.DataFrame(env_records_list),
                meta,
            )

            for key, algorithm in self.algorithms_dict.items():
                self._chromosome_counter = -1
                algorithm.run(1)


class RelatedAgentContainerModel:
    def __init__(
            self,
            container_name: str,
            used_properties: List[str],
            recorded_properties: List[str],
            agent_ids: Callable[[Scenario], List[int]],
    ):
        self.container_name = container_name
        self.used_properties = used_properties
        self.recorded_properties = recorded_properties

        self.agent_ids = agent_ids


class AgentContainerManager:
    """
    The manager class is designed to organize the metadata related to agent agent_lists in the trainer.

    """

    def __init__(self):
        self.agent_containers: List[RelatedAgentContainerModel] = []

    def add_container(
            self,
            container_name: str,
            used_properties: List[str],
            agent_ids: Callable[[Scenario], List[int]],
    ):
        """
        Add a container used in trainer.

        :param container_name:
        :param used_properties:
        :param recorded_properties:
        :param agent_ids:
        :return:
        """
        self.agent_containers.append(
            RelatedAgentContainerModel(container_name, used_properties, [], agent_ids)
        )

    def get_agent_container(
            self, agent_container_name: str
    ) -> RelatedAgentContainerModel:
        for agent_container_model in self.agent_containers:
            if agent_container_model.container_name == agent_container_name:
                return agent_container_model
        raise KeyError(agent_container_name)


class Trainer(BaseModellingManager):
    """
    Individually run agents' parameters
    """

    def __init__(
            self,
            config: "Config",
            scenario_cls: "Optional[Type[Scenario]]",
            model_cls: "Optional[Type[Model]]",
            data_loader_cls: "Optional[Type[DataLoader]]",
            processors: int = 1,
    ):
        super().__init__(
            config=config,
            scenario_cls=scenario_cls,
            model_cls=model_cls,
            data_loader_cls=data_loader_cls,
        )
        self.container_manager = AgentContainerManager()

        self.agent_result_properties: Dict[str, List[str]] = {}

        self.environment_properties: List[str] = []

        self.algorithm_type: str = "ga"
        self.algorithm: Optional[GATrainerAlgorithm] = None
        self.algorithm_instance: Iterator[List[float]] = {}

        self.save_agent_trainer_result = False
        self.save_env_trainer_result = True

        self.model: Optional[Model] = None

        self.agent_result = []
        self.current_algorithm_meta = None
        self.processors = processors

    def add_agent_training_property(
            self,
            container_name: str,
            used_properties: List[str],
            agent_ids: Callable[[Scenario], List[int]],
    ):
        """
        Add a container into the trainer.

        :param container_name: The name of agent container.
        :param used_properties: The properties used in training.
        :param agent_ids: The agent with id contained in `agent_ids` will be trained.
        :return: None
        """
        self.container_manager.add_container(container_name, used_properties, agent_ids)

    def setup(self):
        pass

    def get_trainer_scenario_cls(self):
        """
        Get the class of trainer scenario.
        :return:
        """
        assert self.algorithm_type in {"ga"}

        trainer_scenario_cls: Optional[Union[Type[GATrainerParams]]] = None
        if self.algorithm_type == "ga":
            trainer_scenario_cls = GATrainerParams
        assert trainer_scenario_cls is not None
        return trainer_scenario_cls

    def collect_data(self):
        """
        Set the agent and environment properties to be collected.

        :return:
        """
        pass

    def run(self):
        """
        The main method for Trainer.

        :return:
        """
        self.setup()
        self.collect_data()
        self.pre_run()

        trainer_scenario_cls = self.get_trainer_scenario_cls()
        self.current_algorithm_meta = GATrainerAlgorithmMeta()
        for scenario in self.scenarios:
            self.current_algorithm_meta.trainer_id_scenario = scenario.id
            for trainer_params in self.generate_trainer_params_list(
                    trainer_scenario_cls
            ):
                self.current_algorithm_meta.trainer_params_id = trainer_params.id
                for path_id in range(trainer_params.path_num):
                    self.current_algorithm_meta.path_id = path_id
                    logger.info(
                        f"trainer_id_scenario = {scenario.id}, path_id = {path_id}"
                    )
                    self.run_once_new(scenario, trainer_params)

    def run_once_new(self, scenario: Scenario, trainer_params: Union[GATrainerParams]):
        """
        Use the sko package for optimization.

        :param scenario:
        :param trainer_params:
        :return:
        """

        self.algorithm = GATrainerAlgorithm(trainer_params, self, self.processors)
        self.algorithm.recorded_env_properties = self.environment_properties
        for agent_container in self.container_manager.agent_containers:
            self.algorithm.setup_agent_locations(
                agent_container.container_name,
                agent_container.used_properties,
                agent_container.recorded_properties,
                agent_container.agent_ids(scenario),
            )

        self.algorithm.run(scenario, self.current_algorithm_meta)

    def utility(self, agent: Agent) -> float:
        """
        The utility is to be maximized.

        :param agent:
        :return:
        """
        raise NotImplementedError(
            "Trainer.utility(agent) must be overridden in sub-class!"
        )

    def target_function(self, agent: Agent) -> float:
        """
        The target function to be minimized.

        :param agent:
        :return:
        """
        return -self.utility(agent)

    def add_agent_property(self, agent_list_name: str, prop: str):
        """

        :param agent_list_name:
        :param prop:
        :return:
        """
        self.container_manager.get_agent_container(
            agent_list_name
        ).recorded_properties.append(prop)

    def add_environment_property(self, prop: str):
        """
        Add a property of environment to be recorded in the training voyage.

        :return:
        """
        assert prop not in self.environment_properties
        self.environment_properties.append(prop)

    def generate_scenarios(self):
        """
        Generate Scenarios for trainer

        :return:
        """
        assert self.data_loader is not None
        return self.data_loader.generate_scenarios("trainer")

    def generate_trainer_params_list(
            self, trainer_scenario_cls: Type[GATrainerParams]
    ) -> List[GATrainerParams]:
        """
        Generate Trainer Parameters.

        :return:
        """
        trainer_params_table = self.get_dataframe("trainer_params_scenarios")
        assert isinstance(
            trainer_params_table, pd.DataFrame
        ), "No learning scenarios table specified!"

        trainer_params_raw_list = trainer_params_table.to_dict(orient="records")

        trainer_params_list = []
        for trainer_params_raw in trainer_params_raw_list:
            trainer_params = trainer_scenario_cls.from_dataframe_record(
                trainer_params_raw
            )
            trainer_params_list.append(trainer_params)
        return trainer_params_list
