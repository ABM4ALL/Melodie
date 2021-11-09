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
        # 需要补充注册表中各列数据的变量类型，可以不写数据类型。
        # agent和environment的参数需要写上。写的时候变量类型最好在赋值语句中体现出来。
        # scenarios_dict = {"periods": int, }
        self.register_dataframe('scenarios', 'scenarios.xlsx')  # , scenarios_dict)
        self.register_dataframe('agent_params', 'agent_params.xlsx')

    def register_generated_dataframes(self):
        """
        已完成
        :return:
        """
        # a lot
        # of code
        # to generate wolf_params_df
        # self.register_dataframe('wolf_params', wolf_params_df, wolf_data_type: dict)

        # a lot
        # of code
        # to generate sheep_params_df
        # self.register_dataframe('sheep_params', sheep_params_df, sheep_data_type: dict)

        # 新加的函数

        # 如果在这里生成并注册 --> agent_params，那么，要看生成过程是否跟scenarios有依赖关系。
        # 1. 如果有，列里面需要有scenario_id。
        # 2. 如果没有，怎么办？
        # --> 这里可能不得不出现“框架无法帮忙的复杂”，需要用户自己解决。可以在例子里呈现。
        # table 都改成 dataframe

    def generate_scenarios(self) -> List['Scenario']:
        # 可以隐藏在Melodie.simulator里
        return self.generate_scenarios_from_dataframe('scenarios')
