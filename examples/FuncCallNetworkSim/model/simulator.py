# -*- coding:utf-8 -*-
# @Time: 2021/10/18 9:45
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: register.rst.py
import pandas as pd
from typing import List

from Melodie import Scenario
from Melodie.boost.compiler.boostsimulator import BoostSimulator


class FuncSimulator(BoostSimulator):
    def register_scenario_dataframe(self) -> None:
        self.register_dataframe('scenarios', pd.DataFrame(
            [{"id": i, "reliability": 0.99, "number_of_run": 1, "periods": 100} for i in range(100)]))

    def register_static_dataframes(self):
        pass

    def register_generated_dataframes(self):
        pass

    def generate_scenarios(self) -> List['Scenario']:
        return self.generate_scenarios_from_dataframe("scenarios")

    def generate_agent_params_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame([{"id": i, "reliability": 0.99,
                              "status": 0} for i in range(652)])
