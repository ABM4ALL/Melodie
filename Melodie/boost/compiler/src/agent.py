# -*- coding:utf-8 -*-
# @Time: 2021/10/21 18:22
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: agent.py.py

from Melodie import Agent


class GINIAgent(Agent):

    def setup(self):
        self.id = 0
        self.account = 0.0
        self.productivity = 0.0

    def go_produce(self):
        rand = np.random.random()
        if rand <= self.productivity:
            self.account += 1
        else:
            pass

        return None
