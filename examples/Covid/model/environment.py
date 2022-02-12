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

    def agents_move(self, agent_list: 'AgentList[CovidAgent]', grid: 'Grid') -> None:
        for agent in agent_list:
            agent.move(grid)

    def agents_infection(self, agent_list: 'AgentList[CovidAgent]', grid: "Grid") -> None:
        for agent in agent_list:
            if agent.condition == 0 and agent.condition_next == 1:
                agent.condition = agent.condition_next
        for agent in agent_list:
            neighbors = grid.get_neighbors(agent.x_pos, agent.y_pos, 1, except_self=False)
            if agent.condition == 0:
                infected: int = self.infect_from_neighbor(agent.id, neighbors, grid, agent_list)
                if infected == 1:
                    agent.condition_next = 1
            else:
                pass

    def infect_from_neighbor(self, current_agent_id: int, neighbors: List[Tuple[int, int]], grid: 'Grid',
                             agent_list: "AgentList[CovidAgent]") -> int:
        for neighbor in neighbors:
            agent_ids = grid.get_agent_ids('agent_list', neighbor[0], neighbor[1])
            for agent_id in agent_ids:
                if agent_id == current_agent_id:
                    continue
                if agent_list[agent_id].condition == 1 and random.uniform(0, 1) < self.infection_probability:
                    return 1
        return 0

    def calculate_accumulated_infection(self, agents):
        sum_ = 0
        for agent in agents:
            if agent.condition == 1:
                sum_ += 1
        self.accumulated_infection = sum_
