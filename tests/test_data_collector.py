# -*- coding:utf-8 -*-
# @Time: 2021/9/23 15:53
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: test_data_collector.py


import random
from typing import List

from Melodie import Agent, DataCollector, Environment, Scenario, Simulator, Model, AgentList
from .config import cfg_for_temp

AGENT_NUM_1 = 10
AGENT_NUM_2 = 20


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


class DCTestModel(Model):
    def setup(self):
        self.agent_list1 = self.create_agent_container(TestAgent, 10)
        self.agent_list2 = self.create_agent_container(TestAgent, 20)


class Simulator4Test(Simulator):
    def register_generated_dataframes(self):
        return

    def register_static_dataframes(self):
        return

    def generate_scenarios(self) -> List['Scenario']:
        scenarios = [TestScenario() for i in range(1)]
        for s in scenarios:
            s.manager = self
        return scenarios


data_collector = None


class DataCollector1(DataCollector):
    def setup(self):
        global data_collector
        data_collector = self
        self.add_agent_property("agent_list1", 'a')
        self.add_agent_property("agent_list2", 'b')


def test_model_run():
    Simulator4Test().run(agent_class=TestAgent,
                         environment_class=TestEnv,
                         config=cfg_for_temp,
                         model_class=DCTestModel,
                         scenario_class=TestScenario,
                         data_collector_class=DataCollector1
                         )
    dc: DataCollector = data_collector
    dc.collect(0)
    assert len(dc.agent_properties_dict['agent_list1']) == AGENT_NUM_1
    assert len(dc.agent_properties_dict['agent_list2']) == AGENT_NUM_2
    dc.collect(1)
    assert len(dc.agent_properties_dict['agent_list1']) == AGENT_NUM_1 * 2
    assert len(dc.agent_properties_dict['agent_list2']) == AGENT_NUM_2 * 2
