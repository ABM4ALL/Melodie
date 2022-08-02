# cython: profile=True
# cython:language_level=3
# -*- coding:utf-8 -*-

import random
from typing import List, Tuple

from Melodie import Environment, AgentList, Grid

from .agent import CovidAgent
from .scenario import CovidScenario


class CovidEnvironment(Environment):
    scenario: CovidScenario

    def setup(self):
        self.grid_x_size: int = self.scenario.grid_x_size
        self.grid_y_size: int = self.scenario.grid_y_size
        self.infection_probability: float = self.scenario.infection_probability
        self.accumulated_infection: int = 0

    def agents_move(self, agent_list: "AgentList[CovidAgent]", grid: "Grid"):
        agent_list: AgentList
        agent: CovidAgent
        for agent in agent_list:
            agent.move()

    def agents_infection(self, agent_list: "AgentList[CovidAgent]", grid: "Grid"):
        for agent in agent_list:
            if agent.condition == 1:
                pass
            else:
                neighbors: list = grid.get_neighbor_positions(
                    agent.x, agent.y, 1, moore=True, except_self=False
                )
                agent.condition = self.infect_from_neighbor(
                    agent.id, neighbors, grid, agent_list
                )

    def infect_from_neighbor(
        self,
        current_agent_id: int,
        neighbors: List[Tuple[int, int]],
        grid: Grid,
        agent_list: "AgentList[CovidAgent]",
    ) -> int:

        for neighbor in neighbors:
            x, y = neighbor[0], neighbor[1]
            agent_ids = grid.get_agent_ids(x, y)
            for agent_id, agent_category in agent_ids:
                if agent_id == current_agent_id:
                    continue
                a: CovidAgent = agent_list.get_agent(agent_id)
                if (
                    a.condition == 1
                    and random.uniform(0, 1) < self.infection_probability
                ):
                    return 1
        return 0

    def calculate_accumulated_infection(self, agents: AgentList):
        accumulated = 0
        for agent in agents:
            accumulated += agent.condition
        self.accumulated_infection = accumulated
