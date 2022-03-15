# -*- coding:utf-8 -*-
# @Time: 2022/1/30 11:14
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: df_loader.py
import pandas as pd
from Melodie import DataFrameLoader


class GameOfLifeDataFrameLoader(DataFrameLoader):
    def register_scenario_dataframe(self) -> None:
        self.register_dataframe('simulator_scenarios', pd.DataFrame(
            [{"id": i, "periods": 1000} for i in range(2)]))
