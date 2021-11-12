# -*- coding: utf-8 -*-
__author__ = 'Songmin'

import json
import time
from typing import Dict, List, Tuple

import numpy as np

from Melodie import Model, AgentList
from Melodie.grid import Grid
from Melodie.network import Network, Node
from examples.FuncCallNetworkSim.model.agent import FuncAgent
from .spot import GameOfLifeSpot
from Melodie.visualization import GridVisualizer


class FuncNode(Node):
    def setup(self):
        pass


class GameOfLifeModel(Model):
    def setup(self):
        self.grid = Grid(GameOfLifeSpot, 100, 100)

    def run(self):

        def spot_role(spot: GameOfLifeSpot):
            if spot.alive:
                return 1
            else:
                return -1

        self.visualizer.parse_grid_roles(self.grid, spot_role)
        self.visualizer.start()

        for i in range(self.scenario.periods):
            t0 = time.time()
            self.environment.step(self.grid)
            t1 = time.time()
            print(t1 - t0)
            self.visualizer.parse_grid_roles(self.grid, spot_role)
            self.visualizer.step()

        self.visualizer.parse_grid_roles(self.grid, spot_role)
        self.visualizer.finish()
