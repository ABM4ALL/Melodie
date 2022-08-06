import random
from typing import TYPE_CHECKING

from Melodie import Environment, AgentList
from .agent import CovidAgent
from .scenario import CovidScenario

if TYPE_CHECKING:
    from .grid import CovidGrid
    from .network import CovidNetwork


class CovidEnvironment(Environment):
    scenario: CovidScenario  # 这行代码会被编译吗？

    def setup(self):
        self.s0 = 0
        self.s1 = 0
        self.s2 = 0
        self.s3 = 0
        self.s4 = 0

    def agents_move(self, agents: "AgentList[CovidAgent]"):
        for agent in agents:
            agent.move()

    @staticmethod
    def agents_infection(agents: "AgentList[CovidAgent]", grid: "CovidGrid"):
        for agent in agents:
            agent.infect_from_neighbors(grid, agents)

    def agents_update_vaccination_trust(self, agents: "AgentList[CovidAgent]", network: "CovidNetwork"):
        for agent in agents:
            if random.uniform(0, 1) <= self.scenario.vaccination_ad_percentage:
                agent.update_vaccination_trust_from_ad()
            agent.update_vaccination_trust_from_neighbors(network)

    @staticmethod
    def agents_take_vaccination(agents: "AgentList[CovidAgent]"):
        for agent in agents:
            agent.take_vaccination()

    @staticmethod
    def agents_health_state_transition(agents: "AgentList[CovidAgent]"):
        for agent in agents:
            agent.health_state_transition()

    def calc_population_infection_state(self, agents: "AgentList[CovidAgent]"):
        self.setup()
        for agent in agents:
            if agent.health_state == 0:
                self.s0 += 1
            elif agent.health_state == 1:
                self.s1 += 1
            elif agent.health_state == 2:
                self.s2 += 1
            elif agent.health_state == 3:
                self.s3 += 1
            else:
                self.s4 += 1
