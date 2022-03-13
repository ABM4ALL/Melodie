# -*- coding: utf-8 -*-
__author__ = 'Songmin'

import time

from Melodie import Model, Grid
from .spot import GameOfLifeSpot
from .environment import GameOfLifeEnvironment


class GameOfLifeModel(Model):
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

    def setup_boost(self):

        from Melodie.boost import JITGrid
        self.environment = None
        self.grid = JITGrid(100, 100, GameOfLifeSpot)
        self.visualizer.grid = self.grid
        self.agent_list1: "AgentList[GameOfLifeSpot]" = self.create_agent_container(GameOfLifeSpot, 10)
        self.grid.add_category('agents')
        i = 0
        for agent in self.agent_list1:
            i += 1
            self.grid.add_agent(agent.id, 'agents', 10, i)

    def run(self):
        self.visualizer.parse(self.grid)
        v = 0
        # self.visualizer.set_plot_data(0, 'chart1', {'series1': v, 'series2': 100 - v})
        self.visualizer.start()

        # self.visualizer.set_plot_data(0, 'chart1', {'series1': v, 'series2': 100 - v})
        for i in range(self.scenario.periods):
            t0: float = time.time()
            self.environment.step(self.grid)

            t1: float = time.time()

            self.visualizer.parse(self.grid)
            v += 1
            # self.visualizer.set_plot_data(i, 'chart1', {'series1': v, 'series2': 100 - v})
            self.visualizer.step(i + 1)

            t2: float = time.time()

            print(f"step {i}, {t1 - t0}s for step and {t2 - t1}s for conversion.")

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
