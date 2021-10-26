# -*- coding:utf-8 -*-
# @Time: 2021/9/23 15:43
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: test_table_gen.py.py
import numpy as np

from Melodie import OldConfig, ScenarioManager, Scenario, TableGenerator
from Melodie.run import set_config

set_config(OldConfig('Untitled', with_db=False))


class Scene(Scenario):
    def setup(self):
        self.periods = 100
        self.agent_num = 10
        self.agent_productivity = 1.0
        self.agent_account_min = 0
        self.agent_account_max = 100


class TestTG(TableGenerator):
    def setup(self):
        self.add_agent_param('productivity', self.scenario.agent_productivity)
        self.add_agent_param('account', lambda: float(np.random.randint(self.scenario.agent_account_min,
                                                                        self.scenario.agent_account_max)))


def test_table_generator():
    tg = TestTG(Scene(0))
    tg.setup()
    ret = tg.run()
    print(ret)
    assert ret.shape[0] == 10
