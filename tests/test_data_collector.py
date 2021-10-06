# -*- coding:utf-8 -*-
# @Time: 2021/9/23 15:53
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: test_data_collector.py


import random
from typing import ClassVar

from Melodie import Agent, Config, DataCollector, Environment, run, current_scenario, get_data_collector, Scenario, \
    ScenarioManager


class TestAgent(Agent):
    def setup(self):
        self.a = 123
        self.b = 456
        self.productivity = current_scenario().productivity


class TestEnv(Environment):
    def setup(self):
        pass


class TestScenario(Scenario):
    def setup(self):
        print(self.agent_num)
        self.periods = 1
        self.productivity = random.random()


class TestScenarioManager(ScenarioManager):
    def gen_scenarios(self):
        return [TestScenario(agent_num=100) for i in range(1)]


class DataCollector1(DataCollector):
    def setup(self):
        self.add_agent_property('a')
        self.add_agent_property('b')


def test_model_run():
    run(TestAgent,
        TestEnv,
        config=Config('Untitled', with_db=False),
        scenario_manager_class=TestScenarioManager,
        data_collector_class=DataCollector1
        )
    dc = get_data_collector()
    # dc.collect(0)
    dc.agent_properties_list
    assert len(dc.agent_properties_list) == 100
    dc.collect(1)
    assert len(dc.environment_properties_list) == 2
    assert len(dc.agent_properties_list) == 200
