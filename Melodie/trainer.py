import copy
import logging
import sys
import time
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Literal,
    Optional,
    Tuple,
    Type,
    Union,
    cast,
)

import pandas as pd

from MelodieInfra import Config, MelodieExceptions
from MelodieInfra.core import Agent, AgentList
from MelodieInfra.parallel.parallel_manager import ParallelManager, ThreadParallelManager
from MelodieInfra.utils.utils import underline_to_camel

from .algorithms import AlgorithmParameters
from .algorithms.ga import MelodieGA
from .data_loader import DataLoader
from .model import Model
from .scenario_manager import Scenario
from .simulator import BaseModellingManager
from .utils import run_profile

logger = logging.getLogger(__name__)


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
        self.id_trainer_scenario = 0
        self.id_trainer_params_scenario = 1
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
                super(TrainerAlgorithmMeta, self).__setattr__(key, value)
            else:
                raise MelodieExceptions.General.NoAttributeError(self, key)


class GATrainerAlgorithmMeta(TrainerAlgorithmMeta):
    def __init__(self):
        super().__init__()
        self.id_chromosome = 0
        self._freeze = True


class TargetFcnCache:
    """
    The cache for the pre-computed values.

    Dict:  {(generation_id,
             id_chromosome):
                           {(agent_id,
                             container_name):
                                            function_value
                           }
          }
    """

    def __init__(self):
        self.target_fcn_record: Dict[Tuple[int, int], Dict] = {}
        self.current_generation = -1
        self.current_id_chromosome = -1

    def lookup_agent_target_value(
        self, agent_id: int, container_name: str, generation: int, id_chromosome: int
    ):
        return self.target_fcn_record[(generation, id_chromosome)][
            (agent_id, container_name)
        ]

    def set_agent_target_value(
        self,
        agent_id: int,
        container_name: str,
        value: float,
        generation: int,
        id_chromosome: int,
    ):
        # self.current_target_fcn_value[(agent_id, container_name)] = value
        if (generation, id_chromosome) not in self.target_fcn_record:
            self.target_fcn_record[(generation, id_chromosome)] = {}
        self.target_fcn_record[(generation, id_chromosome)][
            (agent_id, container_name)
        ] = value

    def best_value(
        self, chromosome_num: int, generation: int, agent_id: int, agent_category: int
    ):
        values = [
            self.target_fcn_record[(generation, id_chromosome)][
                (agent_id, agent_category)
            ]
            for id_chromosome in range(chromosome_num)
        ]
        return min(values)


class GATrainerAlgorithm:
    """
    (Internal) The genetic algorithm implementation for the Trainer.

    This class orchestrates the GA process for agent-level parameter training.
    It manages separate GA instances for each agent, distributes simulation
    tasks to parallel workers, caches fitness (utility) scores, and evolves
    each agent's strategy population across generations.
    """

    def __init__(
        self,
        params: GATrainerParams,
        manager: "Trainer" = None,
        processors: int = 1,
        parallel_mode: Literal["process", "thread"] = "process",
    ):
        self.manager = manager
        self.params = params
        self.chromosomes = 20
        self.algorithms_dict: Dict[Tuple[int, str], Union["GA"]] = {}

        self.target_fcn_cache = TargetFcnCache()
        self.agent_container_getters: Dict[str, Callable[[Model], AgentList]] = {}
        self.agent_ids: Dict[str, List[int]] = {}  # {category : [agent_id]}
        self.agent_params_defined: Dict[
            str, List[str]
        ] = {}  # category: [param_name1, param_name2...]
        self.recorded_agent_properties: Dict[
            str, List[str]
        ] = {}  # category: [prop1, prop2...]
        # category: [prop1, prop2...]
        self.recorded_env_properties: List[str] = []

        self._chromosome_counter = 0
        self._current_generation = 0
        self.processors = processors
        self.parallel_mode = parallel_mode

        if self.parallel_mode == "process":
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
        elif self.parallel_mode == "thread":
            self.parallel_manager = ThreadParallelManager(
                cores=self.processors,
                worker_func=self._thread_worker_func,
                worker_init_args=(self.manager,),
            )
            self.parallel_manager.run("trainer")
        else:
            raise ValueError(f"Unknown parallel_mode: {parallel_mode}")

    def _thread_worker_func(
        self, core_id: int, task: Tuple, trainer: "Trainer"
    ) -> Tuple:
        """
        Worker function for thread-based parallelism.
        Runs a single simulation for a given chromosome.
        """
        import logging
        import time
        from Melodie import Environment
        from MelodieInfra.config.global_configs import MelodieGlobalConfig

        # Set up logging for this thread worker (similar to process workers)
        thread_logger = logging.getLogger(f"Trainer-processor-{core_id}")
        
        t0 = time.time()
        chrom, scenario_json, agent_params = task
        thread_logger.debug(f"processor {core_id} got chrom {chrom}")
        
        scenario = trainer.scenario_cls()
        scenario.manager = trainer
        scenario._setup(scenario_json)

        model = trainer.model_cls(trainer.config, scenario)
        model.create()
        model._setup()

        # Apply agent parameters from the GA chromosome
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

        t1 = time.time()
        thread_logger.info(
            f"Processor {core_id}, chromosome {chrom}, time: {MelodieGlobalConfig.Logger.round_elapsed_time(t1 - t0)}s"
        )

        return (chrom, agent_data, env_data)

    def stop(self):
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

    def get_agent_params(self, id_chromosome: int):
        """
        (Internal) Decode the chromosomes for all agents for a given chromosome ID.

        This method constructs the parameter sets for every agent being trained,
        based on the state of their individual GAs at a specific chromosome
        index in the current population.

        :param id_chromosome: The index of the chromosome in the current
            population for all agents.
        :return: A dictionary mapping agent container names to a list of agent
            parameter dictionaries.
        """
        params: Dict[str, List[Dict[str, Any]]] = {
            category: [] for category in self.agent_ids.keys()
        }
        # {category : [{id: 0, param1: 1, param2: 2, ...}]}
        for key, algorithm in self.algorithms_dict.items():
            chromosome_value = algorithm.chrom2x(algorithm.Chrom)[id_chromosome]
            agent_id, agent_category = key
            d = {"id": agent_id}
            for i, param_name in enumerate(self.agent_params_defined[agent_category]):
                # Convert numpy float to native Python float for serialization
                d[param_name] = float(chromosome_value[i])
            params[agent_category].append(d)
        return params

    def target_function_to_cache(
        self,
        agent_target_function_values: Dict[str, List[Dict[str, Any]]],
        generation: int,
        id_chromosome: int,
    ):
        """
        (Internal) Store the output of the target function (utility) in a cache.
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
                    id_chromosome,
                )

    def generate_target_function(
        self, agent_id: int, container_name: str
    ) -> Callable[[], float]:
        """
        (Internal) Create the fitness function for an agent's genetic algorithm.

        This function retrieves the pre-computed utility value from the cache for
        a specific agent and chromosome, allowing the GA to evaluate fitness
        without re-running the simulation.
        """

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

        env_record.update(meta_dict)
        env_record.update(env_data)

        self.manager._write_to_table(
            "csv",
            f"Result_Trainer_{underline_to_camel(container_name)}",
            pd.DataFrame(agent_records[container_name]),
        )

        self.manager._write_to_table(
            "csv",
            "Result_Trainer_Environment",
            pd.DataFrame([env_record]),
        )

        return agent_records, env_record

    def calc_cov_df(
        self,
        agent_container_df_dict: Dict[str, "pd.DataFrame"],
        env_df: "pd.DataFrame",
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
            self.manager._write_to_table(
                "csv",
                f"Result_Trainer_{underline_to_camel(container_name)}_Cov",
                pd.DataFrame(container_agent_record_list),
            )
        env_record = {}
        env_record.update(meta_dict)
        for prop_name in self.recorded_env_properties:
            mean = env_df[prop_name].mean()
            cov = env_df[prop_name].std() / env_df[prop_name].mean()
            env_record.update({prop_name + "_mean": mean, prop_name + "_cov": cov})
        self.manager._write_to_table(
            "csv", "Result_Trainer_Environment_Cov", pd.DataFrame([env_record])
        )

    def pre_check(self, meta):
        """
        Check at the beginning of run()
        :return:
        """
        logger.info(
            f"""Algorithm will run with:
        Meta value: {meta}
        Recording environment parameters: {self.recorded_env_properties}
        Recording Agent agent_lists: {self.recorded_agent_properties}\n"""
        )

    def run(self, scenario: Scenario, meta: Union[GATrainerAlgorithmMeta]):
        self.pre_check(meta)

        for i in range(self.params.generation_num):
            self._current_generation = i
            meta.id_generation = i
            logger.info(
                f"======================="
                f"Scenario {scenario.id} Path {meta.id_path} Generation {i + 1}/{self.params.generation_num}"
                f"======================="
            )
            t0 = time.time()
            for id_chromosome in range(self.params.strategy_population):
                params = self.get_agent_params(id_chromosome)
                self.parallel_manager.put_task(
                    (id_chromosome, scenario.to_json(), params)
                )
                # params_queue.put(
                #     json.dumps()
                # )

            agent_records_collector: Dict[str, List[Dict[str, Any]]] = {
                container_name: [] for container_name in self.agent_ids.keys()
            }
            env_records_list: List[Dict[str, Any]] = []

            for _id_chromosome in range(self.params.strategy_population):
                # v = result_queue.get()
                dt = 0

                (
                    chrom,
                    agents_data,
                    env_data,
                ) = (
                    self.parallel_manager.get_result()
                )  # cloudpickle.loads(base64.b64decode(v))
                t00 = time.time()
                meta.id_chromosome = chrom
                agent_records, env_record = self.record_agent_properties(
                    agents_data, env_data, meta
                )
                for container_name, records in agent_records.items():
                    agent_records_collector[container_name] += records
                env_records_list.append(env_record)
                self.target_function_to_cache(agents_data, i, chrom)

            t1 = time.time()
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
        agent_ids: Optional[Callable[[Scenario], List[int]]] = None,
    ):
        self.container_name = container_name
        self.used_properties = used_properties
        self.recorded_properties = recorded_properties

        self.agent_ids: Optional[Callable[[Scenario], List[int]]] = agent_ids


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
        agent_ids: Optional[Callable[[Scenario], List[int]]],
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
    The ``Trainer`` uses a genetic algorithm to evolve agent-level parameters.

    It is designed for models where agents can "learn" or adapt their
    strategies to maximize a personal objective, defined by a ``utility``
    function.
    """

    def __init__(
        self,
        config: "Config",
        scenario_cls: "Optional[Type[Scenario]]",
        model_cls: "Optional[Type[Model]]",
        data_loader_cls: "Optional[Type[DataLoader]]" = None,
        processors: int = 1,
        parallel_mode: Literal["process", "thread"] = "process",
    ):
        """
        :param config: The project :class:`~Melodie.Config` object.
        :param scenario_cls: The :class:`~Melodie.Scenario` subclass for the model.
        :param model_cls: The :class:`~Melodie.Model` subclass for the model.
        :param data_loader_cls: The :class:`~Melodie.DataLoader` subclass for the
            model.
        :param processors: The number of processor cores to use for parallel
            computation of the genetic algorithm.
        :param parallel_mode: The parallelization mode. ``"process"`` (default)
            uses subprocess-based parallelism, suitable for all Python versions.
            ``"thread"`` uses thread-based parallelism, which is recommended for
            Python 3.13+ (free-threaded/No-GIL builds) for better performance.
        """
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
        self.parallel_mode = parallel_mode

    def add_agent_training_property(
        self,
        agent_list_name: str,
        training_attributes: List[str],
        agent_ids: Callable[[Scenario], List[int]],
    ):
        """
        Register an agent container and its properties for training.

        :param agent_list_name: The name of the agent container attribute on the
            Model object (e.g., 'agents').
        :param training_attributes: A list of agent property names to be tuned by
            the genetic algorithm.
        :param agent_ids: A callable that takes a ``Scenario`` object and returns
            a list of agent IDs to be trained.
        """
        self.container_manager.add_container(
            agent_list_name, training_attributes, agent_ids
        )

    def setup(self):
        """
        A hook for setting up the Trainer.

        This method should be overridden in a subclass to define which agent
        properties to train, using :meth:`add_agent_training_property`.
        """
        pass

    def get_trainer_scenario_cls(self):
        """
        (Internal) Get the parameter class for the trainer's algorithm.
        """
        assert self.algorithm_type in {"ga"}

        trainer_scenario_cls: Optional[Union[Type[GATrainerParams]]] = None
        if self.algorithm_type == "ga":
            trainer_scenario_cls = GATrainerParams
        assert trainer_scenario_cls is not None
        return trainer_scenario_cls

    def collect_data(self):
        """
        (Optional) A hook to define which agent and environment properties to record.

        This is not required for training itself but is useful for saving
        detailed simulation data during the training process. Use
        :meth:`add_agent_property` and :meth:`add_environment_property` to
        register properties.
        """
        pass

    def run(self):
        """
        The main entry point for starting the training process.
        """
        self.setup()
        self.collect_data()
        self.pre_run()

        trainer_scenario_cls = self.get_trainer_scenario_cls()
        self.current_algorithm_meta = GATrainerAlgorithmMeta()
        for scenario in self.scenarios:
            self.current_algorithm_meta.id_trainer_scenario = scenario.id
            for trainer_params in self.generate_trainer_params_list(
                trainer_scenario_cls
            ):
                self.current_algorithm_meta.id_trainer_params_scenario = (
                    trainer_params.id
                )
                for id_path in range(trainer_params.path_num):
                    self.current_algorithm_meta.id_path = id_path
                    logger.info(
                        f"id_trainer_scenario = {scenario.id}, id_path = {id_path}"
                    )
                    self.run_once_new(scenario, trainer_params)

    def run_once_new(self, scenario: Scenario, trainer_params: Union[GATrainerParams]):
        """
        (Internal) Run a single training path.
        """

        self.algorithm = GATrainerAlgorithm(
            trainer_params, self, self.processors, self.parallel_mode
        )
        self.algorithm.recorded_env_properties = self.environment_properties
        for agent_container in self.container_manager.agent_containers:
            self.algorithm.setup_agent_locations(
                agent_container.container_name,
                agent_container.used_properties,
                agent_container.recorded_properties,
                agent_container.agent_ids(scenario),
            )

        self.algorithm.run(scenario, self.current_algorithm_meta)
        self.algorithm.stop()

    def utility(self, agent: Agent) -> float:
        """
        The utility function to be maximized by the trainer.

        This method **must be overridden** in a subclass. It should take an
        ``Agent`` object (representing the final state of an agent after a
        simulation run) and return a single float value representing the
        agent's "utility" or "fitness." The genetic algorithm will attempt to
        find the strategy parameters that maximize this value for each agent.

        :param agent: The ``Agent`` object after a simulation run.
        :return: A float representing the agent's utility.
        """
        raise NotImplementedError(
            "Trainer.utility(agent) must be overridden in sub-class!"
        )

    def target_function(self, agent: Agent) -> float:
        """
        (Internal) The target function to be minimized, which is the negative of utility.
        """
        return -self.utility(agent)

    def add_agent_property(self, agent_list_name: str, prop: str):
        """
        Register an agent property to be recorded during training.

        :param agent_list_name: The name of the agent container.
        :param prop: The name of the agent property to record.
        """
        self.container_manager.get_agent_container(
            agent_list_name
        ).recorded_properties.append(prop)

    def add_environment_property(self, prop: str):
        """
        Register an environment property to be recorded during training.

        :param prop: The name of the environment property to record.
        """
        assert prop not in self.environment_properties
        self.environment_properties.append(prop)

    def generate_scenarios(self):
        """
        Generate scenarios from the ``TrainerScenarios`` table.

        :return: A list of ``Scenario`` objects.
        """
        assert self.data_loader is not None
        return self.data_loader.generate_scenarios("Trainer")

    def generate_trainer_params_list(
        self, trainer_scenario_cls: Type[GATrainerParams]
    ) -> List[GATrainerParams]:
        """
        (Internal) Load GA parameters from the ``TrainerParamsScenarios`` table.
        """

        trainer_params_table = self.get_dataframe("TrainerParamsScenarios")
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
