# -*- coding:utf-8 -*-
# @Time: 2021/10/3 21:00
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: test_lib.py

import time
from Melodie.boost import vectorize, apply, vectorize_2d, apply_2d, py_vectorize_2d
from Melodie import Agent, AgentList, Model, Scenario, OldConfig


class MyAgent(Agent):
    def setup(self):
        self.a = 0.0
        self.b = 0.0
        self.c = 0


class PurePyCell():
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

agent_manager = AgentList(MyAgent, 200, MyModel(config=OldConfig('Untitled')))


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
        a_vec = vectorize(agent_manager.agents, 'b')
        a_vec += 1
        apply(agent_manager.agents, 'a', a_vec)

    t2 = time.time()

    for i in range(steps):
        c_vec = vectorize(agent_manager.agents, 'c')
        c_vec += 1
        apply(agent_manager.agents, 'c', c_vec)

    t3 = time.time()

    print('use_python_time', t1 - t0)
    print('use_cython_time_float', t2 - t1)
    print('use_cython_time_int', t2 - t1)


def compare_collect_attribute_time_2d():
    steps = 200

    t0 = time.time()
    for i in range(steps):
        py_vectorize_2d(pure_py_lst, 'a')

    t1 = time.time()

    for i in range(steps):
        res = vectorize_2d(lst, 'a')
        res += 3
        # res = res.astype('int16')
        apply_2d(lst, 'a', res)
    t2 = time.time()
    print(res)
    for i in range(steps):
        res = vectorize_2d(lst, 'b')
        res += 1
        apply_2d(lst, 'b', res)
    t3 = time.time()
    print(res)
    print('use_dll_gather_float', t3 - t2, 'use_dll_gather_int', t2 - t1, 'use_python_time', t1 - t0)


def test_benchmark():
    compare_collect_attribute_time()
    compare_collect_attribute_time_2d()
