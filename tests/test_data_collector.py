# -*- coding:utf-8 -*-
# @Time: 2021/9/23 15:53
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: test_data_collector.py


import random
from typing import List

import pandas as pd

from Melodie import Agent, DataCollector, Environment, Scenario, Simulator, Model
from .config import cfg_for_temp

AGENT_NUM = 100


class TestAgent(Agent):
    def setup(self):
        self.a = 123
        self.b = 456
        self.productivity = 0  # self.productivity


class TestEnv(Environment):
    def setup(self):
        pass


class TestScenario(Scenario):
    def setup(self):
        print(self.agent_num)
        self.periods = 1
        self.productivity = random.random()


class Simulator4Test(Simulator):
    def generate_agent_params_dataframe(self) -> pd.DataFrame:
        df = pd.DataFrame([{'productivity': random.random(), 'id': i} for i in range(AGENT_NUM)])
        print(df)
        return df

    def generate_scenarios(self) -> List['Scenario']:
        scenarios = [TestScenario(agent_num=AGENT_NUM) for i in range(1)]
        for s in scenarios:
            s.manager = self
        return scenarios


data_collector = None


class DataCollector1(DataCollector):
    def setup(self):
        global data_collector
        self.add_agent_property('a')
        self.add_agent_property('b')
        data_collector = self


def test_model_run():
    Simulator4Test().run(TestAgent,
                         TestEnv,
                         config=cfg_for_temp,
                         model_class=Model,
                         data_collector_class=DataCollector1
                         )
    dc = data_collector
    # dc.collect(0)
    dc.agent_properties_list
    assert len(dc.agent_properties_list) == AGENT_NUM
    dc.collect(1)
    assert len(dc.environment_properties_list) == 2
    assert len(dc.agent_properties_list) == AGENT_NUM * 2
