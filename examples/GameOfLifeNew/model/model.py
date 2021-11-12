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
        self.grid = Grid(GameOfLifeSpot, 50, 50)
        # self.visualizer = GridVisualizer()

    def run(self):

        # self.visualizer.parse_role(self.agent_list.agents, f)
        def spot_role(spot: GameOfLifeSpot):
            if spot.alive:
                return 1
            else:
                return -1

        self.visualizer.parse_grid_roles(self.grid, spot_role)
        self.visualizer.start()

        for i in range(self.scenario.periods):
            self.environment.step(self.grid)

            self.visualizer.parse_grid_roles(self.grid, spot_role)
            self.visualizer.start()

        self.visualizer.parse_grid_roles(self.grid, spot_role)
        self.visualizer.finish()
