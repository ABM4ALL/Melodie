# -*- coding: utf-8 -*-
__author__ = 'Songmin'

import random
from typing import TYPE_CHECKING

import numpy as np

from Melodie import AgentList, Environment
from Melodie.network import Network
from .scenario import FuncScenario

if TYPE_CHECKING:
    from .agent import GINIAgent


class FuncEnvironment(Environment):

    def setup(self):
        self.reliability = self.scenario.reliability
        self.recover_rate = self.scenario.recover_rate

    def step(self, agents: "AgentList", network: "Network"):
        for agent in agents:
            if agent.status == 0:
                if random.random() > self.reliability:
                    agent.fail()
            else:
                if random.random() < self.recover_rate:  # 故障恢复率
                    agent.recover()

        # Propagate fault to next node
        for agent in agents:
            current_node = network.agent_pos(agent.id, 'func')
            if agent.status == 1:
                neighbors: "np.ndarray" = network.get_neighbors(current_node)
                for neighbor_id in neighbors:
                    # There is only one agent at each node, so we could get the agent within an [0] index.
                    agent_on_neighbor_id = list(network.get_agents('func', neighbor_id))[0]
                    agents[agent_on_neighbor_id].fail()

        self.update(agents)
        # for agent in agents:
        #     # for i in range(100): 这个循环没有意义，可以将这个io密集的仿真变成CPU密集。
        #     if agent.status == 0:
        #         if random.random() > agent.reliability:
        #             agent.status = 1
        #     else:
        #         if random.random() > 0.6:  # 故障恢复率0.4
        #             agent.status = 0
        #     if agent.status == 1:
        #         node = network.get_node_by_id(agent.id)
        #         neighbor_ids: "np.ndarray" = network.get_neighbor_ids(node.id)
        #         for neighbor_id in neighbor_ids:
        #             if random.random() > 0.97:  # 故障传播概率 0.03
        #                 agents[neighbor_id].status = 1

    def update(self, agents: "AgentList"):
        """
        Update status
        :return:
        """
        for agent in agents:
            agent.update()

    def get_agents_statistic(self, agents: "AgentList"):
        s = 0
        agent: 'Agent' = None
        for agent in agents:
            s += agent.status
        print(s / 652)
        return s / 652.0
