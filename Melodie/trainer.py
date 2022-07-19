import logging
from typing import Type, List, Optional, ClassVar, Iterator, Union, Tuple, Dict, Callable
import pandas as pd

from Melodie import Model, Scenario, Config, GATrainerParams
from Melodie.algorithms import SearchingAlgorithm
from .algorithms.meta import GATrainerAlgorithmMeta
from .boost.basics import Agent
from .simulator import BaseModellingManager
from .dataframe_loader import DataFrameLoader

logger = logging.getLogger(__name__)


class RelatedAgentContainerModel:
    def __init__(self, container_name: str, used_properties: List[str], recorded_properties: List[str],
                 agent_ids: Callable[[Scenario], List[int]]):
        self.container_name = container_name
        self.used_properties = used_properties
        self.recorded_properties = recorded_properties

        self.agent_ids = agent_ids


class AgentContainerManager:
    """
    The manager class is designed to organize the metadata related to agent containers in the trainer.

    """

    def __init__(self):
        self.agent_containers: List[RelatedAgentContainerModel] = []

    def add_container(self, container_name: str,
                      used_properties: List[str],
                      recorded_properties: List[str],
                      agent_ids: Callable[[Scenario], List[int]]):
        """
        Add a container used in trainer.

        :param container_name:
        :param used_properties:
        :param recorded_properties:
        :param agent_ids:
        :return:
        """
        self.agent_containers.append(
            RelatedAgentContainerModel(container_name, used_properties, recorded_properties, agent_ids))


class Trainer(BaseModellingManager):
    """
    Individually calibrate agents' parameters
    """

    def __init__(
            self,
            config: "Config",
            scenario_cls: "Optional[ClassVar[Scenario]]",
            model_cls: "Optional[ClassVar[Model]]",
            df_loader_cls: "Optional[ClassVar[DataFrameLoader]]",
            processors: int = 1
    ):
        super().__init__(
            config=config,
            scenario_cls=scenario_cls,
            model_cls=model_cls,
            df_loader_cls=df_loader_cls,
        )
        self.container_manager = AgentContainerManager()

        self.agent_result_properties: Dict[str, List[str]] = {}

        self.environment_properties: List[str] = []

        self.algorithm_type: str = "ga"
        self.algorithm: Optional[Type[SearchingAlgorithm]] = None
        self.algorithm_instance: Iterator[List[float]] = {}

        self.save_agent_trainer_result = False
        self.save_env_trainer_result = True

        self.model: Optional[Model] = None

        self.agent_result = []
        self.current_algorithm_meta = None
        self.processors = processors

    def add_container(self, container_name: str, used_properties: List[str],
                      recorded_properties: List[str],
                      agent_ids: Callable[[Scenario], List[int]]):
        """
        Add a container into the trainer.

        :param container_name: The name of agent container.
        :param used_properties: The properties used in training.
        :param recorded_properties: The property to record into the database.
        :param agent_ids: The agent with id contained in `agent_ids` will be trained.
        :return: None
        """
        self.container_manager.add_container(container_name, used_properties, recorded_properties, agent_ids)

    def setup(self):
        pass

    def get_trainer_scenario_cls(self):
        """
        Get the class of trainer scenario.
        :return:
        """
        assert self.algorithm_type in {'ga'}

        trainer_scenario_cls: Union[ClassVar[GATrainerParams]] = None
        if self.algorithm_type == "ga":
            trainer_scenario_cls = GATrainerParams
        assert trainer_scenario_cls is not None
        return trainer_scenario_cls

    def train(self):
        """
        The main method for Trainer.

        :return:
        """
        self.setup()
        self.pre_run()

        trainer_scenario_cls = self.get_trainer_scenario_cls()
        self.current_algorithm_meta = GATrainerAlgorithmMeta()
        for scenario in self.scenarios:
            self.current_algorithm_meta.trainer_scenario_id = scenario.id
            for trainer_params in self.generate_trainer_params_list(trainer_scenario_cls):
                self.current_algorithm_meta.trainer_params_id = trainer_params.id
                for path_id in range(trainer_params.number_of_path):
                    self.current_algorithm_meta.path_id = path_id
                    logger.info(
                        f"trainer_scenario_id = {scenario.id}, path_id = {path_id}"
                    )
                    self.run_once_new(scenario, trainer_params)

    def run_once_new(self, scenario: Scenario, trainer_params: Union[GATrainerParams]):
        """
        Use the sko package for optimization.

        :param scenario:
        :param trainer_params:
        :return:
        """
        from Melodie.algorithms.ga_trainer import GATrainerAlgorithm

        self.algorithm = GATrainerAlgorithm(
            trainer_params,
            self,
            self.processors
        )
        self.algorithm.recorded_env_properties = self.environment_properties
        for agent_container in self.container_manager.agent_containers:
            self.algorithm.add_agent_container(agent_container.container_name,
                                               agent_container.used_properties,
                                               agent_container.recorded_properties,
                                               agent_container.agent_ids(scenario))

        self.algorithm.run(scenario, self.current_algorithm_meta)

    def target_function(self, agent: Agent) -> float:
        """
        The target function to be minimized.

        :param agent:
        :return:
        """
        raise NotImplementedError

    def add_environment_result_property(self, prop: str):
        """

        :return:
        """
        assert prop not in self.environment_properties
        self.environment_properties.append(prop)

    def generate_scenarios(self):
        """
        Generate Scenarios for trainer
        :return:
        """
        assert self.df_loader is not None
        return self.df_loader.generate_scenarios("trainer")

    def generate_trainer_params_list(self, trainer_scenario_cls: ClassVar[GATrainerParams]) \
            -> List[GATrainerParams]:
        """
        Generate Trainer Params-Scenarios.

        :return:
        """
        trainer_params_table = self.get_registered_dataframe(
            "trainer_params_scenarios"
        )
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
