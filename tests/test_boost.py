# -*- coding:utf-8 -*-

import time
from Melodie.boost import vectorize, apply
from Melodie import Agent, AgentList, Model, Scenario
from .config import cfg


class MyAgent(Agent):
    def setup(self):
        self.a = 0.0
        self.b = 0.0
        self.c = 0


class PurePyCell:
    def __init__(self) -> None:
        self.x = 0
        self.y = 0
        self.a = 1
        self.b = 0.1


class MyModel(Model):
    def setup(self):
        self.scenario = Scenario()


XM = 100
YM = 100

agents = [Agent]
pure_py_lst = [[PurePyCell() for i in range(XM)] for j in range(YM)]
lst = pure_py_lst

agent_manager = AgentList(
    MyAgent, MyModel(config=cfg, scenario=Scenario(id_scenario=0))
)


def python_step():
    for agent in agent_manager:
        agent.a += 1
