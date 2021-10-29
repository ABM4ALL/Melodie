# -*- coding: utf-8 -*-
__author__ = 'Songmin'

import random
from typing import TYPE_CHECKING

import numpy as np

from Melodie import AgentManager, Environment
from Melodie.network import Network
from .scenario import FuncScenario

if TYPE_CHECKING:
    from .agent import GINIAgent


class FuncEnvironment(Environment):

    def setup(self):
        scenario: FuncScenario = self.current_scenario()
        # self.trade_num = scenario.trade_num

    def step(self, agents: "AgentManager", network: "Network"):
        for agent in agents:
            if agent.status == 0:
                if random.random() > agent.reliability:
                    agent.status = 1
                    node = network.get_node_by_id(agent.id)
                    neighbors = network.get_neighbors(node)
                    for neighbor in neighbors:
                        agents[neighbor.id].status = 1

    # def step(self, agents: "AgentManager", network: "Network"):
    #     for agent in agents:
    #         if agent.status == 0:
    #             if random.random() > agent.reliability:
    #                 agent.status = 1
    #                 neighbors_ids: "np.ndarray" = network.get_neighbor_ids(agent.id)
    #                 if neighbors_ids is not None:
    #                     for neighbor_id in neighbors_ids:
    #                         agents[neighbor_id].status = 1
