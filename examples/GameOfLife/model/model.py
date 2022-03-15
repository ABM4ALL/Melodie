# -*- coding:utf-8 -*-
# @Time: 2021/9/21 10:28
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: scenario.py

import time

from Melodie import Model, Grid, AgentList
from .spot import GameOfLifeSpot
from .environment import GameOfLifeEnvironment
from .visualizer import GameOfLifeVisualizer


class GameOfLifeModel(Model):
    visualizer: GameOfLifeVisualizer

    def setup(self):
        self.grid = Grid(GameOfLifeSpot, 100, 100)
        with self.define_basic_components():
            self.environment = GameOfLifeEnvironment()
        self.agent_list1: "AgentList[GameOfLifeSpot]" = self.create_agent_container(GameOfLifeSpot, 10)
        self.grid.add_category('agents')
        i = 0
        for agent in self.agent_list1:
            i += 1
            self.grid.add_agent(agent.id, 'agents', 10, i)

    def run(self):
        for current_step in self.routine():
            t0: float = time.time()
            self.environment.step(self.grid)

            t1: float = time.time()

            print(f"step {current_step}, {t1 - t0}s for step")
        self.visualizer.finish()