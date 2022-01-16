# -*- coding:utf-8 -*-
# @Time: 2021/10/18 9:45
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: register.rst.py
import pandas as pd
from typing import List
import sqlalchemy
from Melodie import TableGenerator
from Melodie import Simulator
from .scenario import GiniScenario


class GiniSimulator(Simulator):

    # 1. register_scenario_dataframe单独一个函数注册 --> 必须有，保证数据库里采用预留表名
    # 2. register_static_dataframes: 非必须有，注册其他static dataframes，包括可能的agent参数表
    # 3. register_generated_dataframe: 非必须有，因为也可能在register_static_dataframes注册agent参数表
    #    --> 只有agent_params tables涉及到scenario dependent的问题，其他即便是scenario dependent（比如env的参数），就直接写在scenarios里了。
    #    --> 可能会用到其他static dataframes, but that's no problem
    #    --> 用原来table generator的代码避免考虑id_scenario
    #    --> 考虑多组agent的情况，有一个专门的类(即TableGenerator)，每使用一次就是构造一张表，然后register_dataframe
    # 4. 注册表里的变量类型

    def register_scenario_dataframe(self):
        scenarios_dict = {}
        self.load_dataframe('scenarios', 'scenarios.xlsx', scenarios_dict)

    def register_static_dataframes(self):
        pass
        # 由于已经写进了scenario表中，所以这里不需要任何注册操作了

    def register_generated_dataframes(self):
        """

        :return:
        """
        # 使用了一个上下文管理器，在with中方便地管理表的生成。

        with self.new_table_generator('agent_params', lambda scenario: scenario.agent_num) as g:
            # 生成器。
            # 对于每一个scenario, 生成scenario.agent_num行数据。
            def generator_func(scenario: GiniScenario):
                return {'id': g.increment(), 'productivity': scenario.agent_productivity, 'account': 0.0}

            g.set_row_generator(generator_func)
            g.set_column_data_types({'productivity': sqlalchemy.Float()})
        # 无需调用g的生成表、存储表方法，因为在退出with语句的时候，会自动完成表的生成和存储！




# 保证Simulator管理的所有pandas数据集dataframe的数据类型，与对应数据集的data_type参数指定的数据类型相同
# 同时保证存入数据库时数据类型一致

# 对实际对象如Agent\Scenario赋值的时候，应该直接报错，还是尝试自动类型转换？
# 例如1：agent_params的数据集和数据库表中的字段account为float类型，但是Agent对象为int类型，那么之间自动类型转换？报错？
# 例如2：agent_params的数据集和数据库表中的字段time为pd.Datetime类型，但是Agent对象为int类型(Unix时间戳)
# 方案：自动类型转换并且出warning.
# 数据库： sqlite [integer, REAL, text, date, 二进制]

# agent_params_dict = {'productivity': sqlalchemy.Integer(), 'account': sqlalchemy.Float()}
#
# self.register_dataframe('agent_params', agent_params_list, agent_params_dict)
