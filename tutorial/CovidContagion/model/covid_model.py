from typing import TYPE_CHECKING
from Melodie import Model
from .agent import CovidAgent
from .environment import CovidEnvironment
from .data_collector import CovidDataCollector
from .scenario import CovidScenario
from .grid import CovidSpot, CovidGrid
from .network import CovidEdge, CovidNetwork
from tutorial.CovidContagion.model import data_info as df_info

if TYPE_CHECKING:
    from Melodie import AgentList


class CovidModel(Model):
    scenario: CovidScenario

    def setup(self):
        # self.agents = self.create_agent_list(CovidAgent)
        self.agents: "AgentList[CovidAgent]" = self.create_agent_list(
            CovidAgent,
            self.scenario.agent_num,
            self.scenario.get_dataframe(df_info.agent_params),
        )
        self.environment = self.create_environment(CovidEnvironment)
        self.data_collector = self.create_data_collector(CovidDataCollector)
        self.grid = self.create_grid(CovidGrid, CovidSpot)
        self.config_components()

    def config_components(self):

        self.grid.setup_agent_locations(self.agents)

    def run(self):
        self.scenario.setup_age_group_params()
        for t in self.iterator(self.scenario.periods):
            for hour in range(0, self.scenario.period_hours):
                self.environment.agents_move(self.agents)
                self.environment.agents_infection(self.agents, self.grid)
            self.environment.agents_health_state_transition(self.agents)
            self.environment.calc_agents_health_state(self.agents)
            self.data_collector.collect(t)
        self.data_collector.save()