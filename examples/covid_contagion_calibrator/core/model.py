from typing import TYPE_CHECKING

from Melodie import Model
from .agent import CovidAgent
from .environment import CovidEnvironment
from .data_collector import CovidDataCollector
from .scenario import CovidScenario

if TYPE_CHECKING:
    from Melodie import AgentList


class CovidModel(Model):
    scenario: "CovidScenario"
    agents: "AgentList[CovidAgent]"
    environment: CovidEnvironment
    data_collector: CovidDataCollector

    def create(self) -> None:
        """
        This method is called once at the beginning of the simulation
        to create the core components of the model.
        """
        self.agents = self.create_agent_list(CovidAgent)
        self.environment = self.create_environment(CovidEnvironment)
        self.data_collector = self.create_data_collector(CovidDataCollector)

    def setup(self) -> None:
        """
        This method is called once after `create` to set up the initial state
        of the model components.
        """
        self.agents.setup_agents(self.scenario.agent_num)
        self.environment.setup_infection(self.agents)

    def run(self) -> None:
        """
        This method defines the main simulation loop that runs for `scenario.period_num` periods.
        """
        for t in self.iterator(self.scenario.period_num):
            self.environment.agents_interaction(self.agents)
            self.environment.agents_recover(self.agents)
            self.environment.update_population_stats(self.agents)
            self.data_collector.collect(t)
        self.data_collector.save()
