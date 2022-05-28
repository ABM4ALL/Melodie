# -*- coding:utf-8 -*-
import time

from Melodie import Model, Grid, AgentList, GridAgent
from .spot import GameOfLifeSpot
from .environment import GameOfLifeEnvironment
from .visualizer import GameOfLifeVisualizer


class GameOfLifeModel(Model):
    visualizer: GameOfLifeVisualizer

    def setup(self):
        self.grid = Grid(GameOfLifeSpot, 100, 100)
        with self.define_basic_components():
            self.environment = GameOfLifeEnvironment()
        self.agent_list1: "AgentList[GridAgent]" = self.create_agent_container(GridAgent, 10)
        self.grid.add_category('agents')

        i = 0
        for agent in self.agent_list1:
            i += 1
            agent.x = 10
            agent.y = i
            self.grid.add_agent(agent, 'agents')

    def run(self):
        for current_step in self.routine():
            t0: float = time.time()
            self.environment.step(self.grid)

            t1: float = time.time()

            print(f"step {current_step}, {t1 - t0}s for step")
        self.visualizer.finish()
