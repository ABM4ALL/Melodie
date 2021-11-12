# -*- coding:utf-8 -*-
# @Time: 2021/9/21 10:28
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: simulator.py.py
from typing import List

from Melodie import Scenario


class FuncScenario(Scenario):
    def setup(self):
        self.agent_num = 652
        self.reliability = 0.99

    def properties_as_parameters(self) -> List[Scenario.BaseParameter]:
        return [Scenario.NumberParameter("reliability", 0.99, 0, 1, 0.001),
                Scenario.NumberParameter("recover_rate", 0.8, 0, 1, 0.001)]
