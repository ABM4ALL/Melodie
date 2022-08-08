from typing import TYPE_CHECKING

from Melodie import Model, Network, Edge
from tutorial.CovidContagion.source import data_info
from .agent import CovidAgent
from .data_collector import CovidDataCollector
from .environment import CovidEnvironment
from .grid import CovidSpot, CovidGrid
from .network import CovidNetwork, CovidEdge
from .scenario import CovidScenario

if TYPE_CHECKING:
    from Melodie import AgentList


class CovidModel(Model):
    scenario: CovidScenario

    def create(self):
        self.agents: "AgentList[CovidAgent]" = self.create_agent_list(CovidAgent)
        self.environment = self.create_environment(CovidEnvironment)
        self.data_collector = self.create_data_collector(CovidDataCollector)
        self.grid = self.create_grid(CovidGrid, CovidSpot)
        self.network = self.create_network()

    def setup(self):
        self.agents.setup_agents(self.scenario.agent_num, self.scenario.get_dataframe(data_info.agent_params))
        self.grid.setup_params(self.scenario.grid_x_size, self.scenario.grid_y_size)
        self.grid.setup_agent_locations(self.agents)
        self.network.setup_agent_connections([self.agents], "barabasi_albert_graph", {"m": 1})

        # self.network.set_network_type(self.scenario.network_type)
        # self.network.set_network_params({'k': self.scenario.network_param_k, 'p': self.scenario.network_param_p})
        # self.network.setup_agent_connections(self.agents)

    def run(self):
        for t in self.iterator(self.scenario.periods):
            for hour in range(0, self.scenario.period_hours):
                self.environment.agents_move(self.agents)
                self.environment.agents_infection(self.agents, self.grid)
            # self.environment.agents_update_vaccination_trust(self.agents, self.network)
            # self.environment.agents_take_vaccination(self.agents)
            self.environment.agents_health_state_transition(self.agents)
            self.environment.calc_population_infection_state(self.agents)
            self.data_collector.collect(t)
        self.data_collector.save()
