# -*- coding:utf-8 -*-
# @Time: 2021/9/21 10:28
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: scenario.py.py
from typing import List

from Melodie.scenariomanager import ScenarioManager, Scenario


class GiniScenario(Scenario):
    def setup(self):
        self.periods = 200
        self.agent_num = 100
        self.agent_account_min = 0.0
        self.agent_account_max = 100.0
        self.agent_productivity = 0.5
        self.trade_num = 100
        self.rich_win_prob = 0.8


class GiniScenarioManager(ScenarioManager):
    def gen_scenarios(self) -> List[Scenario]:
        """
        Only generate one scenario here.
        :return:
        """

        scenarios = [GiniScenario() for i in range(3)]
        for i, scenario in enumerate(scenarios):
            scenario.rich_win_prob = 0.1 * (i + 1) + 0.5  # 0.1,0.2,...0.9
        return scenarios