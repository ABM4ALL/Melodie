# -*- coding:utf-8 -*-
# @Time: 2021/11/18 16:25
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: test_model.py
from Melodie.basic import MelodieException
from Melodie import Agent, Model, Scenario
from .config import cfg


class TestAgent(Agent):
    def setup(self):
        self.a = 123
        self.b = 456
        self.productivity = 0


class TestModel(Model):
    def setup(self):
        self.agent_list1 = self.create_agent_container(TestAgent, 10)
        self.agent_list1[2].id = 1
        self.agent_list1[3].id = 1

        self.agent_list1[4].id = 5
        self.agent_list1[5].id = 5


def test_agent_container_id_check():
    tm = TestModel(config=cfg, scenario=Scenario(id_scenario=0))
    tm.setup()
    try:
        tm.check_agent_containers()
    except MelodieException as e:
        assert e.id == 1303
