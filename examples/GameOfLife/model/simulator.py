# -*- coding:utf-8 -*-
# @Time: 2021/10/18 9:45
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: dataframe_loader.py
import pandas as pd
from typing import List

from Melodie import Scenario, Simulator
from .visualizer import GameOfLifeVisualizer


class GameOfLifeSimulator(Simulator):
    def setup(self):
        self.visualizer = GameOfLifeVisualizer()
        self.visualizer.setup()

