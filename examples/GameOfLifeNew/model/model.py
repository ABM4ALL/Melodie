# -*- coding: utf-8 -*-
__author__ = 'Songmin'

import json
import time
from typing import Dict, List, Tuple

import numpy as np

from Melodie import Model, AgentList
from Melodie.grid import Grid, build_jit_class
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

    def setup_boost(self):
        self.environment = None
        self.grid = build_jit_class(100, 100)
        self.visualizer.grid = self.grid

    # def spot_role(self, spot: "GameOfLifeSpot"):
    #     if spot.alive:
    #         return 1
    #     else:
    #         return -1

    def run(self):
        self.visualizer.parse(self.grid)
        self.visualizer.start()

        for i in range(self.scenario.periods):
            t0: float = time.time()
            self.environment.step(self.grid)

            t1: float = time.time()
            print(t1 - t0)
            t0:float = time.time()
            self.visualizer.parse(self.grid)
            t1:float = time.time()
            print("parsing time", t1 - t0)
            self.visualizer.step()

        print(self.grid._spots)
        self.visualizer.parse(self.grid)
        self.visualizer.finish()
