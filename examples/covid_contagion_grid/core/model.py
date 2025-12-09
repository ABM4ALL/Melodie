from typing import TYPE_CHECKING

from Melodie import Model

from .agent import CovidAgent
from .data_collector import CovidDataCollector
from .environment import CovidEnvironment
from .grid import CovidGrid, CovidSpot
from .scenario import CovidScenario

if TYPE_CHECKING:
    from Melodie import AgentList


class CovidModel(Model):
    """
    The Model class assembles all components: agents, environment, grid, and data collector.
    """

    scenario: "CovidScenario"
    agents: "AgentList[CovidAgent]"
    environment: CovidEnvironment
    data_collector: CovidDataCollector
    grid: CovidGrid

    def create(self) -> None:
        """
        Create component instances.
        """
        self.agents = self.create_agent_list(CovidAgent)
        self.environment = self.create_environment(CovidEnvironment)
        self.data_collector = self.create_data_collector(CovidDataCollector)
        self.grid = self.create_grid(CovidGrid, CovidSpot)

    def setup(self) -> None:
        """
        Setup the model components.
        """
        # 1. Initialize agents based on scenario parameter
        self.agents.setup_agents(self.scenario.agent_num)
        
        # 2. Setup grid dimensions and apply properties (like stay_prob)
        self.grid.setup_params(width=self.scenario.grid_x_size, height=self.scenario.grid_y_size)
        
        # 3. Place agents randomly on the grid
        self.grid.setup_agent_locations(self.agents)
        
        # 4. Seed initial infections
        self.environment.seed_infection(self.agents)

    def run(self) -> None:
        """
        The main simulation loop.
        """
        for t in self.iterator(self.scenario.period_num):
            self.environment.agents_move(self.agents)
            self.environment.agents_infect(self.agents)
            self.environment.agents_recover(self.agents)
            self.environment.update_population_stats(self.agents)
            self.data_collector.collect(t)
        self.data_collector.save()
