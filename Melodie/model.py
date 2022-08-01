import logging
from contextlib import contextmanager
from typing import ClassVar, Optional, Union

import pandas as pd

from .basic import MelodieExceptions, show_prettified_warning, show_link
from .boost.agent_list import AgentList, BaseAgentContainer, AgentDict
from .boost.basics import Agent, Environment
from .boost.grid import GridAgent
from .config import Config
from .data_collector import DataCollector
from .db import create_db_conn, DBConn
from .scenario_manager import Scenario
from .table_generator import TableGenerator
from .visualizer import Visualizer

logger = logging.getLogger(__name__)


class ModelRunRoutine:
    """
    This is an simple iterator
    """

    def __init__(self, max_step: int, model: "Model"):
        self._current_step = 0
        self._max_step = max_step
        self.model: "Model" = model

    def __iter__(self):
        return self

    def __next__(self):
        if self._current_step >= self._max_step:
            raise StopIteration
        self.model.visualizer_step(self._current_step)
        self._current_step += 1
        return self._current_step

    def __del__(self):
        """
        Remove circular reference before deletion
        :return:
        """
        self.model = None


class Model:
    def __init__(
        self,
        config: "Config",
        scenario: "Scenario",
        run_id_in_scenario: int = 0,
        visualizer: Visualizer = None,
    ):

        self.scenario = scenario
        self.config = config

        self.environment: Optional[Environment] = None
        self.data_collector: Optional[DataCollector] = None
        self.table_generator: Optional[TableGenerator] = None
        self.run_id_in_scenario = run_id_in_scenario

        self.network = None
        self.visualizer = visualizer

    def __del__(self):
        """
        Remove circular reference before deletion
        :return:
        """
        self.visualizer = None

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

    def create_db_conn(self) -> "DBConn":
        return create_db_conn(self.config)

    def check_grid_agents_initialized(self):
        """
        Check if grid agents are initialized
        :return:
        """
        for prop_name, prop in self.__dict__.items():
            if isinstance(prop, BaseAgentContainer):
                for agent in prop:
                    if isinstance(agent, GridAgent):
                        assert agent.grid is not None, (
                            "GridAgents created before running"
                            "should be added onto the Grid."
                        )

    @contextmanager
    def define_basic_components(self):
        """

        Environment or DataCollector should not be defined more than once
        :return:
        """
        MelodieExceptions.Assertions.IsNone("self.environment", self.environment)
        MelodieExceptions.Assertions.IsNone("self.data_collector", self.data_collector)

        yield self
        # MelodieExceptions.Assertions.Type('self.environment', self.environment, Environment)
        self.environment.model = self
        self.environment.scenario = self.scenario
        self.environment.setup()
        if self.data_collector is not None:
            MelodieExceptions.Assertions.Type(
                "self.data_collector", self.data_collector, DataCollector
            )
            self.data_collector.model = self
            self.data_collector.setup()
        # self.check_grid_agents_initialized()

    def create_agent_container(
        self,
        agent_class: ClassVar["Agent"],
        initial_num: int,
        params_df: pd.DataFrame = None,
        container_type: str = "list",
    ) -> Union[AgentList]:
        """
        Create a container for agents
        :param agent_class:
        :param initial_num: Initial number of agents
        :param params_df:
        :param container_type:
        :return:
        """
        from Melodie import AgentList

        agent_container_class: Union[ClassVar[AgentList], None]
        if container_type == "list":
            agent_container_class = AgentList
        elif container_type == "dict":
            agent_container_class = AgentDict
        else:
            raise NotImplementedError(
                f"Container type '{container_type}' is not valid!"
            )

        container = agent_container_class(agent_class, initial_num, model=self)
        if params_df is not None:
            container.set_properties(params_df)
        else:
            show_prettified_warning(
                f"No dataframe set for the {agent_container_class.__name__}.\n\t"
                + show_link()
            )
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

    def routine(self, periods: int):
        return ModelRunRoutine(periods, self)

    def visualizer_step(self, current_step: int):
        if (self.visualizer is not None) and (current_step > 0):
            self.visualizer.step(current_step)
