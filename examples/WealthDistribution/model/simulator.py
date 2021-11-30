# -*- coding:utf-8 -*-
# @Time: 2021/10/18 9:45
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: simulator.py
import pandas as pd
from typing import List

import sqlalchemy

from Melodie import Simulator


class GiniSimulator(Simulator):

    def register_static_dataframes(self):
        scenarios_dict = {}
        self.register_dataframe('scenarios', 'scenarios.xlsx', scenarios_dict)

    def register_generated_dataframes(self):
        """

        :return:
        """
        #  保证Simulator管理的所有pandas数据集dataframe的数据类型，与对应数据集的data_type参数指定的数据类型相同
        #  同时保证存入数据库时数据类型一致

        #  对实际对象如Agent\Scenario赋值的时候，应该直接报错，还是尝试自动类型转换？
        # 例如1：agent_params的数据集和数据库表中的字段account为float类型，但是Agent对象为int类型，那么之间自动类型转换？报错？
        # 例如2：agent_params的数据集和数据库表中的字段time为pd.Datetime类型，但是Agent对象为int类型(Unix时间戳)
        # 方案：自动类型转换并且出warning.
        # 数据库： sqlite [integer, REAL, text, date, 二进制]

        agent_params_dict = {'productivity': sqlalchemy.Integer(), 'account': sqlalchemy.Float()}

        self.register_dataframe('agent_params', 'agent_params.xlsx', agent_params_dict)

    def generate_scenarios(self) -> List['Scenario']:
        # 这个函数在用户端去掉，隐藏在Melodie.simulator里
        return self.generate_scenarios_from_dataframe('scenarios')
