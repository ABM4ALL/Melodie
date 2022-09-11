import random
from typing import TYPE_CHECKING

from Melodie import NetworkAgent
from tutorial.CovidContagion.source.agent import CovidAgent

if TYPE_CHECKING:
    from Melodie import AgentList
    from .scenario import CovidNetworkScenario


class CovidNetworkAgent(CovidAgent, NetworkAgent):
    scenario: "CovidNetworkScenario"

    def set_category(self):
        self.category = 0

    def setup(self):
        self.age_group = 0
        self.health_state = 0

    def infection(self, agents: "AgentList[CovidNetworkAgent]"):
        neighbors = self.network.get_neighbors(self)
        for neighbor_category, neighbor_id in neighbors:
            neighbor_agent: "CovidNetworkAgent" = agents.get_agent(neighbor_id)
            if neighbor_agent.health_state == 1:
                if random.uniform(0, 1) < self.scenario.infection_prob:
                    self.health_state = 1
                    break
