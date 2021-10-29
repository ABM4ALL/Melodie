# -*- coding:utf-8 -*-
# @Time: 2021/10/18 9:45
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: simulator.py
import pandas as pd
from typing import List

from Melodie.boost.compiler.boostsimulator import BoostSimulator


class FuncSimulator(BoostSimulator):
    def register_static_tables(self):
        pass

    def create_scenarios_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame([{"id": i, "reliability": 0.99} for i in range(1)])

    def generate_scenarios(self) -> List['Scenario']:
        return super(BoostSimulator, self).generate_scenarios()

    def generate_agent_params_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame([{"id": i, "reliability": 0.99,
                              "status": 0} for i in range(652)])
