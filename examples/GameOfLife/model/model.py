# -*- coding: utf-8 -*-
__author__ = 'Songmin'

import time

import numpy as np

from Melodie import Model
from Melodie.grid import Grid
from .spot import GameOfLifeSpot


class GameOfLifeModel(Model):
    def setup(self):
        self.grid = Grid(GameOfLifeSpot, 100, 100)

    def setup_boost(self):
        from Melodie.boost import JITGrid
        self.environment = None
        self.grid = JITGrid(100, 100, GameOfLifeSpot)
        self.visualizer.grid = self.grid
        self.agent_list: "AgentList[GameOfLifeSpot]" = np.zeros((10,), dtype=[('alive', 'i8')])
        self.agent_list[0]['alive'] = True

    def run(self):
        # self.studio.parse(self.grid)
        # self.studio.start()

        for i in range(self.scenario.periods):
            t0: float = time.time()
            self.environment.step(self.grid, self.agent_list)

            t1: float = time.time()

            # arr: 'np.ndarray' = self.grid.to_2d_array() # get_2d_array()['alive']

            # self.studio.parse(self.grid)
            # self.studio.step(i)

            t2: float = time.time()

            print(f"step {i}, {t1 - t0}s for step and {t2 - t1}s for conversion.")

        print(self.grid._spots)

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
