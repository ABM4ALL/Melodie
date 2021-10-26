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
        # 需要补充注册表中各列数据的变量类型
        self.register_table('scenarios', 'scenarios.xlsx')
        self.register_table('agent_params', 'agent_params.xlsx')

    def register_generated_tables(self):
        # 新加的函数

        # 如果在这里生成并注册 --> agent_params，那么，要看生成过程是否跟scenarios有依赖关系。
        # 1. 如果有，列里面需要有scenario_id。
        # 2. 如果没有，怎么办？
        # --> 这里可能不得不出现“框架无法帮忙的复杂”，需要用户自己解决。可以在例子里呈现。

        pass






    def generate_scenarios(self) -> List['Scenario']:
        # 可以隐藏在Melodie.simulator里
        return super(GiniSimulator, self).generate_scenarios()




    def generate_agent_params_dataframe(self) -> pd.DataFrame:
        # 去掉了，这件事应该在model里做
        return self.get_registered_table('agent_params')
