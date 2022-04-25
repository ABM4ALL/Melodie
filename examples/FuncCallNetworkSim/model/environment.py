# -*- coding: utf-8 -*-
__author__ = 'Songmin'

import random

import numpy as np
from .scenario import FuncScenario
from .agent import FuncAgent
from Melodie import AgentList, Environment
from Melodie.network import OldNetwork


class FuncEnvironment(Environment):
    scenario: FuncScenario

    def setup(self):
        self.reliability = self.scenario.reliability
        self.recover_rate = self.scenario.recover_rate

    def step(self, agents: "AgentList", network: "OldNetwork"):
        for agent in agents:
            if agent.status == 0:
                if random.random() > self.reliability:
                    agent.fail()
            else:
                if random.random() < self.recover_rate:
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

    def update(self, agents: "AgentList"):
        """
        Update status
        :return:
        """
        for agent in agents:
            agent.update()

    def get_agents_statistic(self, agents: "AgentList"):
        s = 0
        agent: FuncAgent = None
        for agent in agents:
            s += agent.status
        print(s / 652)
        return s / 652.0
