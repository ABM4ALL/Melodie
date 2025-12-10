import logging
from typing import List, Optional, Type, TypeVar, Union

from MelodieInfra import (
    DBConn,
    MelodieExceptions,
    create_db_conn,
    show_link,
    show_prettified_warning,
)

# from .boost.grid import Grid, Spot
from MelodieInfra.config.config import Config

# from .boost.agent_list import AgentList, BaseAgentContainer, AgentDict
from MelodieInfra.core import (
    Agent,
    AgentList,
    BaseAgentContainer,
    Environment,
    Grid,
    Spot,
)

from .data_collector import DataCollector
from .network import Edge, Network
from .scenario_manager import Scenario
from .table_generator import DataFrameGenerator
from .visualizer import Visualizer

logger = logging.getLogger(__name__)

EnvironmentType = TypeVar("EnvironmentType", bound=Environment)
AgentType = TypeVar("AgentType", bound=Agent)
GridType = TypeVar("GridType", bound=Grid)
SpotType = TypeVar("SpotType", bound=Spot)
NetworkType = TypeVar("NetworkType", bound=Network)
DataCollectorType = TypeVar("DataCollectorType", bound=DataCollector)


class ModelRunRoutine:
    """
    An iterator for the model's main run loop.

    When ``Model.iterator()`` is called, a ``ModelRunRoutine`` object is
    created. It yields an integer representing the current step, ranging from
    0 to ``max_step - 1``.
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
        Clean up resources to avoid circular references.
        """
        self.model = None


class Model:
    """
    The base class for a Melodie model.

    The model class is the central component that orchestrates the simulation.
    It follows a structured lifecycle managed by three main methods: ``create()``,
    ``setup()``, and ``run()``. The ``Simulator`` calls ``create()`` and then
    ``setup()`` once at the beginning of a simulation run. The ``run()`` method
    is then called to execute the main simulation loop.

    To implement a custom model, users should inherit from this class and
    override these three methods.
    """

    def __init__(
        self,
        config: "Config",
        scenario: "Scenario",
        run_id_in_scenario: int = 0,
        visualizer: "Visualizer" = None,
    ):
        """
        :param config: The framework configuration object.
        :param scenario: The scenario object providing parameters for the model run.
        :param run_id_in_scenario: The ID of the current simulation run for this
            scenario. It is an integer in ``[0, scenario.run_num - 1]``.
        :param visualizer: The visualizer instance, if visualization is enabled.
        """

        self.scenario = scenario
        self.config: "Config" = config

        self.environment: Optional[Environment] = None
        self.data_collector: Optional[DataCollector] = None
        self.table_generator: Optional[DataFrameGenerator] = None
        self.run_id_in_scenario = run_id_in_scenario

        self.network = None
        self.visualizer: "Visualizer" = visualizer
        self.initialization_queue: List[
            Union["AgentList", "Grid", "Environment", DataCollector, Network]
        ] = []

    def __del__(self):
        """
        Clean up resources to avoid circular references.
        """
        self.visualizer = None

    def create(self):
        """
        Create and initialize model components.

        This method is the first part of the model's initialization process. It
        should be used to create all the necessary components of the model, such
        as agent lists, the environment, grid/network structures, and the data
        collector.
        """
        pass

    def setup(self):
        """
        Set up the initial state of the model.

        This method is the second part of the model's initialization process,
        called after ``create()``. It should be used to establish the initial
        state of the model's components, such as setting initial agent
        properties or creating network connections.
        """
        pass

    def create_db_conn(self) -> "DBConn":
        """
        Create a database connection using the project configuration.

        :return: A ``DBConn`` object for database interaction.
        """
        return create_db_conn(self.config)

    def create_agent_list(
        self,
        agent_class: Type[AgentType],
    ) -> AgentList[AgentType]:
        """
        Create an :class:`~Melodie.AgentList` object.

        A model can contain multiple agent lists for different types of agents.

        :param agent_class: The class of the agent to be contained in the list.
        :return: An :class:`~Melodie.AgentList` object.
        """
        return AgentList(agent_class, model=self)

    def create_environment(self, env_class: Type[EnvironmentType]) -> EnvironmentType:
        """
        Create the environment for the model.

        A model should have only one environment.

        :param env_class: The class of the environment to be created.
        :return: The created environment object.
        """
        env = env_class()
        env.model = self
        env.scenario = self.scenario
        self.initialization_queue.append(env)
        return env

    def create_grid(
        self,
        grid_cls: Optional[Type[GridType]] = None,
        spot_cls: Optional[Type[SpotType]] = None,
    ) -> GridType:
        """
        Create a grid for spatial simulations.

        :param grid_cls: The class of the grid. Defaults to
            :class:`~MelodieInfra.core.grid.Grid`.
        :param spot_cls: The class of the spots that make up the grid. Defaults
            to :class:`~MelodieInfra.core.grid.Spot`.
        :return: The created grid object.
        """
        grid_cls = grid_cls if grid_cls is not None else Grid
        spot_cls = spot_cls if spot_cls is not None else Spot
        grid = grid_cls(spot_cls, self.scenario)
        self.initialization_queue.append(grid)
        return grid

    def create_network(
        self,
        network_cls: Optional[Type[NetworkType]] = None,
        edge_cls: Type[Edge] = None,
    ):
        """
        Create a network for agent interactions.

        :param network_cls: The class of the network. Defaults to
            :class:`~Melodie.Network`.
        :param edge_cls: The class for edges in the network. Defaults to
            :class:`~Melodie.Edge`.
        :return: The created network object.
        """
        if network_cls is None:
            network_cls = Network
        network = network_cls(model=self, edge_cls=edge_cls)
        self.initialization_queue.append(network)
        return network

    def create_data_collector(self, data_collector_cls: Type[DataCollectorType]) -> DataCollectorType:
        """
        Create the data collector for the model.

        :param data_collector_cls: The DataCollector class, which must be a custom
            class inheriting from :class:`~Melodie.DataCollector`.
        :return: A ``DataCollector`` object.
        """
        data_collector = data_collector_cls()
        data_collector.model = self
        data_collector.scenario = self.scenario
        data_collector.config = self.config
        self.initialization_queue.append(data_collector)
        return data_collector

    def create_agent_container(
        self,
        agent_class: Type["Agent"],
        initial_num: int,
        params_df: "pd.DataFrame" = None,
        container_type: str = "list",
    ) -> Union[AgentList, "AgentDict"]:
        """
        Create a container for agents.

        .. note::
            This is a legacy method. The recommended way to create agent
            containers is to use :meth:`create_agent_list`.

        :param agent_class: The class of the agent.
        :param initial_num: The initial number of agents to create.
        :param params_df: A pandas DataFrame to initialize agent properties.
        :param container_type: A string specifying the container type, either
            "list" or "dict". "dict" is not yet implemented.
        :return: The created agent container.
        """
        from Melodie import AgentList

        agent_container_class: Union[Type[AgentList], Type["AgentDict"], None]
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
        Check that all agents across all containers have unique IDs.
        """
        for prop_name, prop in self.__dict__.items():
            if isinstance(prop, BaseAgentContainer):
                all_ids = prop.all_agent_ids()
                if len(set(all_ids)) < len(all_ids):
                    raise MelodieExceptions.Agents.AgentIDConflict(
                        prop_name, all_ids)

    def run(self):
        """
        The main entry point for the simulation run.

        This method should be overridden in a subclass to define the model's
        primary logic, which is executed after ``create()`` and ``setup()``.
        """
        pass

    def iterator(self, period_num: int):
        """
        Get an iterator for the simulation loop.

        The iterator yields the current period, from ``0`` to ``period_num - 1``,
        and handles visualizer updates at each step.

        :param period_num: The total number of periods for the simulation run.
        :return: A ``ModelRunRoutine`` iterator object.
        """
        return ModelRunRoutine(period_num, self)

    def _visualizer_step(self, current_step: int):
        """
        If a visualizer is present, advance it by one step.
        """
        if (self.visualizer is not None) and (current_step > 0):
            self.visualizer.step(current_step)

    def init_visualize(self):
        """
        A hook for initializing the visualizer.

        This method should be overridden in the model subclass if custom
        visualization setup is required.
        """
        # raise NotImplementedError

    def _setup(self):
        """
        The main setup routine that calls ``create()``, ``setup()``, and the
        ``_setup()`` methods of all initialized components in order.
        """
        self.create()
        self.setup()
        for component_to_init in self.initialization_queue:
            component_to_init._setup()
