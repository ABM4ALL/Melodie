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
    MyAgent, 200, MyModel(config=cfg, scenario=Scenario(id_scenario=0))
)


def python_step():
    for agent in agent_manager:
        agent.a += 1


def compare_collect_attribute_time():
    steps = 500 * 5  # 200 agents, 500 steps, 5 experiments

    t0 = time.time()
    for i in range(steps):
        python_step()
    t1 = time.time()

    for i in range(steps):
        a_vec = vectorize(agent_manager.agents, "b")
        a_vec += 1
        apply(agent_manager.agents, "a", a_vec)

    t2 = time.time()

    for i in range(steps):
        c_vec = vectorize(agent_manager.agents, "c")
        c_vec += 1
        apply(agent_manager.agents, "c", c_vec)

    t3 = time.time()

    print("use_python_time", t1 - t0)
    print("use_cython_time_float", t2 - t1)
    print("use_cython_time_int", t2 - t1)
