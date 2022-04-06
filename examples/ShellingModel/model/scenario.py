# -*- coding:utf-8 -*-
# @Time: 2021/9/21 10:28
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: scenario.py
from Melodie import Scenario


class ShellingModelScenario(Scenario):
    def setup(self):
        self.periods = 100
        self.desired_sametype_neighbors = 3
        pass
