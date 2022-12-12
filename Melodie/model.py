import logging
from typing import Optional, Union, Type, List

import pandas as pd

from MelodieInfra import create_db_conn, DBConn, MelodieExceptions, show_prettified_warning, show_link
from .boost.agent_list import AgentList, BaseAgentContainer, AgentDict
from .boost.basics import Agent, Environment
from .boost.grid import Grid, Spot
from MelodieInfra.config.config import Config
from .data_collector import DataCollector

from .scenario_manager import Scenario
from .table_generator import DataFrameGenerator
from .network import Network, Edge
from .visualizer import Visualizer

logger = logging.getLogger(__name__)


class ModelRunRoutine:
    """
    This is an simple iterator for model run

    """

    def __init__(self, max_step: int, model: "Model"):
        self._current_step = -1
        self._max_step = max_step
        self.model: "Model" = model

    def __iter__(self):
        return self

    def __next__(self):
        if self._current_step >= self._max_step - 1:
            raise StopIteration
        self.model._visualizer_step(self._current_step)
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
        self.table_generator: Optional[DataFrameGenerator] = None
        self.run_id_in_scenario = run_id_in_scenario

        self.network = None
        self.visualizer: "Visualizer" = visualizer
        self.initialization_queue: List[
            Union[AgentList, Grid, Environment, DataCollector, Network]
        ] = []

    def __del__(self):
        """
        Remove circular reference before deletion

        :return:
        """
        self.visualizer = None

    def setup(self):
        """
        General method for setting up the model.

        :return: None
        """
        pass

    def create(self):
        """
        This method will be called automatically before setup()

        :return: None
        """
        pass

    def create_db_conn(self) -> "DBConn":
        """
        Create database connection for model

        :return: DBConn object
        """
        return create_db_conn(self.config)

    def create_agent_list(
            self,
            agent_class: Type["Agent"],
    ):
        """
        Create one agent list of model.

        :param agent_class: The class of desired agent type.
        :return: Agentlist object created
        """
        return AgentList(agent_class, model=self)

    def create_environment(self, env_class: Type["Environment"]):
        """
        Create the environment of model.

        :param env_class:
        :return: Environment object created
        """
        env = env_class()
        env.model = self
        env.scenario = self.scenario
        self.initialization_queue.append(env)
        return env

    def create_grid(self, grid_cls: Type["Grid"] = None, spot_cls: Type["Spot"] = None):
        """
        Create the grid of model

        :param grid_cls:
        :param spot_cls:
        :return: Grid object created
        """
        grid_cls = grid_cls if grid_cls is not None else Grid
        spot_cls = spot_cls if spot_cls is not None else Spot
        grid = grid_cls(spot_cls, self.scenario)
        self.initialization_queue.append(grid)
        return grid

    def create_network(
            self, network_cls: Type["Network"] = None, edge_cls: Type["Edge"] = None
    ):
        """
        Create the network of model

        :param network_cls:
        :param edge_cls:
        :return: Network object created
        """
        if network_cls is None:
            network_cls = Network
        network = network_cls(edge_cls)
        self.initialization_queue.append(network)
        return network

    def create_data_collector(self, data_collector_cls: Type["DataCollector"]):
        """
        Create the data collector of model.

        :param data_collector_cls: The custom datacollector class.
        :return: Datacollector object created.
        """
        data_collector = data_collector_cls()
        data_collector.model = self
        data_collector.scenario = self.scenario
        self.initialization_queue.append(data_collector)
        return data_collector

    def create_agent_container(
            self,
            agent_class: Type["Agent"],
            initial_num: int,
            params_df: pd.DataFrame = None,
            container_type: str = "list",
    ) -> Union[AgentList]:
        """
        Create a container for agents

        :param agent_class:
        :param initial_num: Initial number of agents
        :param params_df:   pandas DataFrame
        :param container_type: "list" or "dict"
        :return: Agent container created
        """
        from Melodie import AgentList

        agent_container_class: Union[Type[AgentList], Type[AgentDict], None]
        if container_type == "list":
            agent_container_class = AgentList
        elif container_type == "dict":
            agent_container_class = AgentDict
        else:
            raise NotImplementedError(
                f"Container type '{container_type}' is not valid!"
            )

        container = agent_container_class(agent_class, model=self)
        if params_df is not None:
            container.set_properties(params_df)
        else:
            show_prettified_warning(
                f"No dataframe set for the {agent_container_class.__name__}.\n\t"
                + show_link()
            )
        self.initialization_queue.append(container)
        return container

    def _check_agent_containers(self):
        """
        Check the agent agent_lists in the model.
        Check list is:
        - Each agent, no matter which container it was in, should have a unique id.

        :return: None
        """
        for prop_name, prop in self.__dict__.items():
            if isinstance(prop, BaseAgentContainer):
                all_ids = prop.all_agent_ids()
                if len(set(all_ids)) < len(all_ids):
                    raise MelodieExceptions.Agents.AgentIDConflict(prop_name, all_ids)

    def run(self):
        """
        Model run. Be sure to inherit this method on your model.

        :return: None
        """
        pass

    def iterator(self, period_num: int):
        """
        Return an iterator which iterates from `0` to `period_num-1`. In each iteration, the iterator updates the
        visualizer if it exists.

        :param period_num: How many periods will this model run.
        :return: None
        """
        return ModelRunRoutine(period_num, self)

    def _visualizer_step(self, current_step: int):
        """
        If visualizer is defined, make it step.

        :param current_step:
        :return:
        """
        if (self.visualizer is not None) and (current_step > 0):
            self.visualizer.step(current_step)

    def init_visualize(self):
        """
        Be sure to implement it if you would like to use visualizer.

        :return:
        """
        raise NotImplementedError

    def _setup(self):
        """
        Wrapper of setup()

        :return:
        """
        self.create()
        self.setup()
        for component_to_init in self.initialization_queue:
            component_to_init._setup()
