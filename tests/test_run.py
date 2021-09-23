# -*- coding:utf-8 -*-
# @Time: 2021/9/18 9:18
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: test_model.py
import random
from typing import ClassVar

from Melodie.agent import Agent
from Melodie.agent_manager import AgentManager
from Melodie.environment import Environment

from Melodie.run import run, current_scenario
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
        return [TestScenario(agent_num=100) for i in range(100)]


def test_model_run():
    run(TestAgent,
        TestEnv,
        scenario_manager_class=TestScenarioManager)
