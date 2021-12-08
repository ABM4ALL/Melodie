# -*- coding:utf-8 -*-
# @Time: 2021/10/18 9:45
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: simulator.py
import pandas as pd
from typing import List

from Melodie import Scenario, Simulator


class FuncSimulator(Simulator):
    def register_static_dataframes(self):
        pass

    def register_scenario_dataframe(self) -> None:
        """
        Register scenario dataframe
        :return:
        """
        self.register_dataframe('scenarios', pd.DataFrame(
            [{"id": i, "periods": 1000} for i in range(2)]))
