import logging
import sys
from contextlib import contextmanager
from typing import ClassVar, Optional, Union

import pandas as pd

from . import DB
from .agent import Agent
from .agent_list import AgentList, BaseAgentContainer
from .basic import MelodieExceptions
from .config import Config
from .data_collector import DataCollector
from .environment import Environment
from .scenario_manager import Scenario
from .table_generator import TableGenerator
from .db import create_db_conn
from .visualization import Visualizer

logger = logging.getLogger(__name__)


class Model:
    def __init__(self,
                 config: 'Config',
                 scenario: 'Scenario',
                 run_id_in_scenario: int = 0,
                 visualizer: Visualizer = None
                 ):

        self.scenario = scenario
        self.config = config

        self.environment: Optional[Environment] = None
        self.data_collector: Optional[DataCollector] = None
        self.table_generator: Optional[TableGenerator] = None
        self.run_id_in_scenario = run_id_in_scenario

        self.network = None
        self.visualizer = visualizer

    def setup(self):
        """
        general method for setting up the model.
        :return:
        """
        pass

    def setup_boost(self):
        """
        setup method for boosting.
        :return:
        """
        pass

    def current_scenario(self) -> 'Scenario':
        MelodieExceptions.Assertions.Type("self.scenario", self.scenario, Scenario)
        return self.scenario

    def create_db_conn(self) -> 'DB':
        return create_db_conn(self.config)

    def setup_environment(self):
        self.environment = self.environment_class()
        self.environment.model = self
        self.environment.setup()

    @contextmanager
    def define_basic_components(self):
        """

        Environment or DataCollector should not be defined more than once
        :return:
        """
        MelodieExceptions.Assertions.IsNone('self.environment', self.environment)
        MelodieExceptions.Assertions.IsNone('self.data_collector', self.data_collector)

        yield self
        MelodieExceptions.Assertions.Type('self.environment', self.environment, Environment)
        self.environment.model = self
        self.environment.setup()
        if self.data_collector is not None:
            MelodieExceptions.Assertions.Type('self.data_collector', self.data_collector, DataCollector)
            self.data_collector.model = self
            self.data_collector.setup()

    def create_agent_container(self, agent_class: ClassVar['Agent'], initial_num: int,
                               params_df: pd.DataFrame = None,
                               container_type: str = "list") -> Union[AgentList]:
        """
        Create a container for agents
        :param agent_class:
        :param initial_num: Initial number of agents
        :param params_df:
        :param container_type:
        :return:
        """
        agent_container_class: Union[ClassVar[AgentList], None] = None
        if container_type == "list":
            agent_container_class = AgentList
        else:
            raise NotImplementedError(f"Container type '{container_type}' is not valid!")

        container = agent_container_class(agent_class, initial_num, model=self)
        if params_df is not None:
            container.set_properties(params_df)
            container.post_setup()
        else:
            logger.warning(f"No dataframe set for the {agent_container_class.__name__}")
        return container

    def check_agent_containers(self):
        """
        Check the agent containers in the model.
        Check list is:
        - Each agent, no matter which container it was in, should have a unique id.

        :return:
        """
        for prop_name, prop in self.__dict__.items():
            if isinstance(prop, BaseAgentContainer):
                all_ids = prop.all_agent_ids()
                if len(set(all_ids)) < len(all_ids):
                    raise MelodieExceptions.Agents.AgentIDConflict(prop_name, all_ids)

    def run(self):
        pass

    def run_boost(self):
        pass
