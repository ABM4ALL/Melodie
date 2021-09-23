# -*- coding:utf-8 -*-
# @Time: 2021/9/23 15:53
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: test_data_collector.py


import random
from typing import ClassVar

from Melodie.agent import Agent
from Melodie.agent_manager import AgentManager
from Melodie.datacollector import DataCollector
from Melodie.environment import Environment

from Melodie.run import run, current_scenario, get_data_collector
from Melodie.scenariomanager import Scenario, ScenarioManager


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
        scenario_manager_class=TestScenarioManager,
        data_collector_class=DataCollector1
        )
    agent_df, env_df = get_data_collector().collect(0)
    assert agent_df.shape[0] == 100
    agent_df, env_df = get_data_collector().collect(1)
    assert env_df.shape[0] == 2
    assert agent_df.shape[0] == 200

