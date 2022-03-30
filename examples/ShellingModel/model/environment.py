from Melodie import Environment, Grid, GridAgent, AgentList
from .agent import ShellingModelAgentTypeA, ShellingModelAgentTypeB
from .scenario import ShellingModelScenario


class ShellingModelEnvironment(Environment):
    scenario: ShellingModelScenario

    def setup(self):
        pass

    def calc_satisfactory(self, grid: Grid, agent_list_a: "AgentList[ShellingModelAgentTypeA]",
                          agent_list_b: "AgentList[ShellingModelAgentTypeB]"):
        a_unsatisfied = []
        b_unsatisfied = []
        for agent_a in agent_list_a:
            if not agent_a.satisfy_with_neighbors(grid):
                a_unsatisfied.append(agent_a.id)
        for agent_b in agent_list_b:
            if not agent_b.satisfy_with_neighbors(grid):
                b_unsatisfied.append(agent_b.id)
        return a_unsatisfied, b_unsatisfied
