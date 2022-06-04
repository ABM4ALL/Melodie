from typing import List

from Melodie import Environment, Grid, AgentList
from .agent import ShellingModelAgentTypeA, ShellingModelAgentTypeB, BaseGridAgent
from .scenario import ShellingModelScenario


class ShellingModelEnvironment(Environment):
    scenario: ShellingModelScenario

    def setup(self):
        pass

    def calc_satisfactory(
        self,
        grid: Grid,
        agent_list_a: "AgentList[ShellingModelAgentTypeA]",
        agent_list_b: "AgentList[ShellingModelAgentTypeB]",
    ):
        """
        Get all unsatisfied agents

        :param grid:
        :param agent_list_a:
        :param agent_list_b:
        :return:
        """
        a_unsatisfied = []
        b_unsatisfied = []
        for agent_a in agent_list_a:
            if not agent_a.satisfy_with_neighbors(grid):
                a_unsatisfied.append(agent_a.id)
        for agent_b in agent_list_b:
            if not agent_b.satisfy_with_neighbors(grid):
                b_unsatisfied.append(agent_b.id)
        return a_unsatisfied, b_unsatisfied

    def unsatisfied_move_to_empty(
        self,
        unsatisfied_agent_id: List[int],
        agent_list: "AgentList[BaseGridAgent]",
        grid: Grid,
    ):
        for b_id in unsatisfied_agent_id:
            pos = grid.find_empty_spot()
            agent = agent_list.get_agent(b_id)

            grid.move_agent(agent, agent.category, pos[0], pos[1])
            agent.x = pos[0]
            agent.y = pos[1]
