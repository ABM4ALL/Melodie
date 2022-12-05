from typing import TYPE_CHECKING

from Melodie import Model
from tutorial.CovidContagion.source import data_info
from .agent import CovidNetworkAgent
from .data_collector import CovidNetworkDataCollector
from .environment import CovidNetworkEnvironment
from .scenario import CovidNetworkScenario

if TYPE_CHECKING:
    from Melodie import AgentList


class CovidNetworkModel(Model):
    scenario: CovidNetworkScenario

    def create(self):
        self.agents: "AgentList[CovidNetworkAgent]" = self.create_agent_list(
            CovidNetworkAgent
        )
        self.environment = self.create_environment(CovidNetworkEnvironment)
        self.data_collector = self.create_data_collector(CovidNetworkDataCollector)
        self.network = self.create_network()

    def setup(self):
        self.agents.setup_agents(
            agents_num=self.scenario.agent_num,
            params_df=self.scenario.get_dataframe(data_info.agent_params),
        )
        self.network.setup_agent_connections(
            agent_lists=[self.agents],
            network_type=self.scenario.network_type,
            network_params=self.scenario.get_network_params(),
        )

    def run(self):
        for period in self.iterator(self.scenario.period_num):
            self.environment.agents_infection(self.agents)
            self.environment.agents_health_state_transition(self.agents)
            self.environment.calc_population_infection_state(self.agents)
            self.data_collector.collect(period)
        self.data_collector.save()
