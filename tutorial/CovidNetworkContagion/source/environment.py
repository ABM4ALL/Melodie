from Melodie import Environment, AgentList
from .agent import CovidAgent
from .scenario import CovidScenario


class CovidEnvironment(Environment):
    scenario: CovidScenario

    def setup(self):
        self.s0 = 0
        self.s1 = 0
        self.s2 = 0
        self.s3 = 0

    def agents_infection(self, agents: "AgentList[CovidAgent]"):
        for agent in agents:
            if agent.health_state == 0:
                agent.infection(agents)

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
            else:
                self.s3 += 1
