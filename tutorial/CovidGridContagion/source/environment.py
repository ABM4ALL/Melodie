from Melodie import AgentList
from tutorial.CovidContagion.source.environment import CovidEnvironment
from .agent import CovidGridAgent
from .scenario import CovidGridScenario


class CovidGridEnvironment(CovidEnvironment):
    scenario: CovidGridScenario

    def agents_move(self, agents: "AgentList[CovidGridAgent]"):
        for agent in agents:
            agent.move()

    def agents_infection(self, agents: "AgentList[CovidGridAgent]"):
        for agent in agents:
            if agent.health_state == 0:
                agent.infection(agents)
