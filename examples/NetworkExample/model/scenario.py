# -*- coding:utf-8 -*-
# @Time: 2021/9/21 10:28
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: register.rst.py.py

from Melodie import Scenario


class GiniScenario(Scenario):
    def setup(self):
        self.periods = 200
        self.agent_num = 100
        self.agent_account_min = 0.0
        self.agent_account_max = 100.0
        self.agent_productivity = 0.5
        self.trade_num = 100
        self.rich_win_prob = 0.8


