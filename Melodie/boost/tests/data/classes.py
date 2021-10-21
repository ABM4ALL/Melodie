# -*- coding:utf-8 -*-
# @Time: 2021/10/21 14:58
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: classes.py
import random
from typing import Tuple

from Melodie import Agent


class ClsTest:
    def __init__(self):
        self.b = 0

    def property_access(self):
        self.a = self.b
        self.c = self.b

    def go_money_transfer(self, agent_list: 'AgentManager'):
        trade_num = self.trade_num
        for sub_period in range(0, int(trade_num)):
            # agents: "Tuple[Agent]" = agent_list.random_sample(2)
            agents = agent_list.random_sample(2)
            agent_1: "Agent" = agents[0]
            agent_2: "Agent" = agents[1]

            who_win = 0
            rand = random.random()
            RICH = 0
            POOR = 1
            if rand <= self.win_prob:
                who_win = RICH
            else:
                who_win = POOR

            if agent_1.account >= agent_2.account and who_win == RICH:
                self.go_give_money(agent_2, agent_1)
            elif agent_1.account < agent_2.account and who_win == RICH:
                self.go_give_money(agent_1, agent_2)
            elif agent_1.account >= agent_2.account and who_win == POOR:
                self.go_give_money(agent_1, agent_2)
            elif agent_1.account < agent_2.account and who_win == POOR:
                self.go_give_money(agent_2, agent_1)
            else:
                pass
        return None
