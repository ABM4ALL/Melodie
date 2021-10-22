# -*- coding:utf-8 -*-
# @Time: 2021/10/18 9:45
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: simulator.py
import pandas as pd
from typing import List

from Melodie import Simulator


class GiniSimulator(Simulator):
    def register_static_tables(self):
        self.register_static_table('agent_params', 'params.xlsx')
        self.register_static_table('scenarios', 'scenarios2.xlsx')

    def create_scenarios_dataframe(self) -> pd.DataFrame:
        return self.get_static_table('scenarios')

    def generate_scenarios(self) -> List['Scenario']:
        return super(GiniSimulator, self).generate_scenarios()

    def generate_agent_params_dataframe(self) -> pd.DataFrame:
        return self.get_static_table('agent_params')
