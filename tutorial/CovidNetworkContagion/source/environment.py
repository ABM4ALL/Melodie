from Melodie import AgentList
from tutorial.CovidContagion.source.environment import CovidEnvironment
from .agent import CovidNetworkAgent
from .scenario import CovidNetworkScenario


class CovidNetworkEnvironment(CovidEnvironment):
    scenario: CovidNetworkScenario

    def agents_infection(self, agents: "AgentList[CovidNetworkAgent]"):
        for agent in agents:
            if agent.health_state == 0:
                agent.infection(agents)
