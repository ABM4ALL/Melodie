import numpy as np
from typing import TYPE_CHECKING

from Melodie import Environment

if TYPE_CHECKING:
    from Melodie import AgentList, Network
    from .scenario import OpinionDynamicsScenario
    from .agent import OpinionDynamicsAgent


class OpinionDynamicsEnvironment(Environment):
    scenario: "OpinionDynamicsScenario"
    agent: "OpinionDynamicsAgent"

    def agents_communication(
        self, agent_list: "AgentList[OpinionDynamicsAgent]", network: "Network"
    ) -> None:
        for agent in agent_list:
            agent.reset_communication_track()
            agent_neighbors = network._get_neighbor_positions(agent.id, "agent_list")
            for neighbor in agent_neighbors:
                if np.random.uniform(0, 1) <= self.scenario.communication_prob:
                    agent.update_opinion_level_with_neighbor(agent_list[neighbor[1]])
                    break
                else:
                    pass

    def calc_average_opinion_level(
        self, agent_list: "AgentList[OpinionDynamicsAgent]"
    ) -> None:
        self.average_opinion_level = 0
        sum_opinion_level = 0
        for agent in agent_list:
            sum_opinion_level += agent.opinion_level
        self.average_opinion_level = sum_opinion_level / self.scenario.agent_num
