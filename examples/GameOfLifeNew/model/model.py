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

    def run(self):
        import matplotlib.pyplot as plt
        # self.visualizer.parse(self.grid)
        # self.visualizer.start()
        plt.figure()
        plt.ion()

        for i in range(self.scenario.periods):
            plt.cla()
            t0: float = time.time()
            self.environment.step(self.grid)

            t1: float = time.time()

            arr: 'np.ndarray' = self.grid.get_2d_array()['alive']

            # self.visualizer.parse(self.grid)
            # self.visualizer.step()

            t2: float = time.time()

            print(f"step {i}, {t1 - t0}s for step and {t2 - t1}s for conversion.")
            plt.imshow(arr, cmap='hot')
            plt.pause(0.01)

        print(self.grid._spots)
        # self.visualizer.parse(self.grid)
        # self.visualizer.finish()
