# -*- coding:utf-8 -*-
# @Time: 2021/10/18 9:45
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: dataframe_loader.rst.py
import pandas as pd

from Melodie import Simulator
from .visualizer import FuncCallSimVisualizer


class FuncSimulator(Simulator):
    def setup(self):
        self.visualizer = FuncCallSimVisualizer()

    # def generate_agent_params_dataframe(self) -> pd.DataFrame:
    #     return pd.DataFrame([{"id": i, "reliability": 0.99,
    #                           "status": 0} for i in range(652)])
