# -*- coding: utf-8 -*-
__author__ = 'Songmin'

import time

from Melodie import Model, GridAgent, AgentList
from Melodie import Grid
from .environment import GameOfLifeSpot
from .environment import GameOfLifeEnvironment


class GameOfLifeModel(Model):
    def setup(self):
        self.grid = Grid(GameOfLifeSpot, 200, 200)
        with self.define_basic_components():
            self.environment = GameOfLifeEnvironment()
        self.agent_list1: "AgentList[GameOfLifeSpot]" = self.create_agent_container(GridAgent, 10)
        self.grid.add_category('agents')
        i = 0
        for agent in self.agent_list1:
            i += 1
            agent.x = 10
            agent.y = i
            self.grid.add_agent(agent, 'agents')

    def run(self):
        # self.visualizer.parse(self.grid)
        # self.visualizer.start()
        self.scenario.periods = 100
        for i in range(self.scenario.periods):
            t0: float = time.time()
            self.environment.step(self.grid)

            t1: float = time.time()

            # self.visualizer.parse(self.grid)
            # self.visualizer.step(i)

            t2: float = time.time()

            print(f"step {i}, {t1 - t0}s for step and {t2 - t1}s for conversion.")

        # print(self.grid._spots)

    # def run_with_matplotlib(self):
    #     import matplotlib.pyplot as plt
    #     # self.studio.parse(self.grid)
    #     # self.studio.start()
    #     plt.figure()
    #     plt.ion()
    #
    #     for i in range(self.scenario.periods):
    #         plt.cla()
    #         t0: float = time.time()
    #         self.environment.step(self.grid)
    #
    #         t1: float = time.time()
    #
    #         arr: 'np.ndarray' = self.grid.get_2d_array()['alive']
    #
    #         # self.studio.parse(self.grid)
    #         # self.studio.step()
    #
    #         t2: float = time.time()
    #
    #         print(f"step {i}, {t1 - t0}s for step and {t2 - t1}s for conversion.")
    #         plt.imshow(arr, cmap='hot')
    #         plt.pause(0.01)
    #
    #     print(self.grid._spots)
    # self.studio.parse(self.grid)
    # self.studio.finish()
