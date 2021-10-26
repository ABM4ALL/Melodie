# -*- coding:utf-8 -*-
# @Time: 2021/10/19 19:11
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: ast_demo.py.py

# -*- coding: utf-8 -*-
__author__ = 'Songmin'

import random
import numpy as np

from Melodie import Agent, Model, Environment, AgentList


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


class GiniEnvironment(Environment):

    def setup(self):
        scenario: 'GiniScenario' = self.current_scenario()
        self.trade_num = scenario.trade_num
        self.win_prob = scenario.rich_win_prob
        self.total_wealth = 0
        self.gini = 0

    def go_money_produce(self, agent_list: "AgentList"):

        al = agent_list
        for agent in al:
            agent.go_produce()

        return None

    def go_give_money(self, agent_from: 'GINIAgent', agent_to: 'GINIAgent'):

        if agent_from.account == 0:
            pass
        else:
            agent_from.account -= 1
            agent_to.account += 1

        return None

    def go_money_transfer(self, agent_list: 'AgentList'):
        trade_num = self.trade_num
        for sub_period in range(0, int(trade_num)):
            agent_1: 'Agent' = None
            agent_2: 'Agent' = None
            agent_1, agent_2 = agent_list.random_sample(2)

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

    def calc_gini(self, account_list: 'np.ndarray'):

        # x = account_list
        N = len(account_list)
        s = 0
        i = 0
        for xi in account_list:
            s += xi * (N - i)
            i += 1
        B = s / (N * np.sum(account_list))

        return (1 + (1 / N) - 2 * B)

    def calc_wealth_and_gini(self, AgentList: 'AgentList'):

        account_list: "np.ndarray" = np.zeros(len(AgentList))
        i = 0
        for agent in AgentList:
            account_list[i] = agent.account
            i += 1

        self.total_wealth = sum(account_list)
        self.gini = self.calc_gini(account_list)

        return None


class GiniModel(Model):

    def run(self):
        # dc = self.data_collector
        for t in range(0, self.scenario.periods):
            self.environment.go_money_produce(self.agent_list)
            self.environment.go_money_transfer(self.agent_list)
            self.environment.calc_wealth_and_gini(self.agent_list)
        #     dc.collect(t)
        # dc.save()
