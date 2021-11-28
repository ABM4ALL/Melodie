# -*- coding:utf-8 -*-
# @Time: 2021/10/18 9:45
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: simulator.py
import pandas as pd
from typing import List

from Melodie import Simulator


class GiniSimulator(Simulator):

    def register_static_dataframes(self):

        scenarios_dict = {"periods": int, }
        self.register_dataframe('scenarios', 'scenarios.xlsx', scenarios_dict)

    def register_generated_dataframes(self):

        agent_params_dict = {}
        self.register_dataframe('agent_params', 'agent_params.xlsx', agent_params_dict)

    def generate_scenarios(self) -> List['Scenario']:
        # 这个函数在用户端去掉，隐藏在Melodie.simulator里
        return self.generate_scenarios_from_dataframe('scenarios')





