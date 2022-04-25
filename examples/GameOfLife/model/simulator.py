# -*- coding:utf-8 -*-
# @Time: 2021/10/18 9:45
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: simulator.py

from Melodie import Simulator
from .visualizer import GameOfLifeVisualizer


class GameOfLifeSimulator(Simulator):
    def setup(self):
        self.visualizer = GameOfLifeVisualizer()
        self.visualizer.setup()

