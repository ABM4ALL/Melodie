# -*- coding:utf-8 -*-

from Melodie import Simulator
from .visualizer import GameOfLifeVisualizer


class GameOfLifeSimulator(Simulator):
    def setup(self):
        self.visualizer = GameOfLifeVisualizer()
        self.visualizer.setup()

