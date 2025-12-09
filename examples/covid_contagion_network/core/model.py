from typing import TYPE_CHECKING

from Melodie import Model

from .agent import CovidAgent
from .data_collector import CovidDataCollector
from .environment import CovidEnvironment
from .scenario import CovidScenario

if TYPE_CHECKING:
    from Melodie import AgentList


class CovidModel(Model):
    """
    Network contagion model.
    Demonstrates the use of `Melodie.Network` for agent interaction.
    """

    scenario: "CovidScenario"
    agents: "AgentList[CovidAgent]"
    environment: CovidEnvironment
    data_collector: CovidDataCollector

    def create(self) -> None:
        """
        Create model components: Agents, Environment, DataCollector, and Network.
        """
        self.agents = self.create_agent_list(CovidAgent)
        self.environment = self.create_environment(CovidEnvironment)
        self.data_collector = self.create_data_collector(CovidDataCollector)
        
        # Create an empty network structure
        self.network = self.create_network()

    def setup(self) -> None:
        """
        Setup model components and build the network.
        """
        # 1. Initialize agents
        self.agents.setup_agents(self.scenario.agent_num)

        # 2. Build network connections based on scenario parameters
        # This uses NetworkX generators under the hood.
        self.network.setup_agent_connections(
            agent_lists=[self.agents],
            network_type=self.scenario.network_type,
            network_params=self.scenario.get_network_params(),
        )

        # 3. Seed initial infections
        self.environment.seed_infection(self.agents)

    def run(self) -> None:
        """
        Main simulation loop.
        """
        for t in self.iterator(self.scenario.period_num):
            self.environment.spread_on_network(self.agents)
            self.environment.recover(self.agents)
            self.environment.update_population_stats(self.agents)
            self.data_collector.collect(t)
        self.data_collector.save()
