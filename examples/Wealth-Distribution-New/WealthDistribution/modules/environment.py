# -*- coding: utf-8 -*-
__author__ = 'Songmin'

import random
from typing import TYPE_CHECKING

import numpy as np

from Melodie.agent_manager import AgentManager
from Melodie.environment import Environment
from Melodie.run import current_scenario
from ..model.scenario import GiniScenario

if TYPE_CHECKING:
    from .agent import GINIAgent


class GiniEnvironment(Environment):

    def setup(self):
        scenario: GiniScenario = current_scenario()
        self.trade_num = scenario.trade_num
        self.win_prob = scenario.rich_win_prob
        self.total_wealth = 0
        self.gini = 0

    def go_MoneyProduce(self, AgentList):

        for agent in AgentList:
            agent.go_produce()

        return None

    def go_GiveMoney(self, AgentFrom: 'GINIAgent', AgentTo: 'GINIAgent'):

        if AgentFrom.account == 0:
            pass
        else:
            AgentFrom.account -= 1
            AgentTo.account += 1

        return None

    def go_MoneyTransfer(self, AgentList:'AgentManager'):
        for sub_period in range(0, self.trade_num):
            [Agent1, Agent2] = AgentList.random_sample(2)

            WhoWin = 0
            rand = np.random.uniform(0, 1)
            if rand <= self.win_prob:
                WhoWin = "Rich"
            else:
                WhoWin = "Poor"

            if Agent1.account >= Agent2.account and WhoWin == "Rich":
                self.go_GiveMoney(Agent2, Agent1)
            elif Agent1.account < Agent2.account and WhoWin == "Rich":
                self.go_GiveMoney(Agent1, Agent2)
            elif Agent1.account >= Agent2.account and WhoWin == "Poor":
                self.go_GiveMoney(Agent1, Agent2)
            elif Agent1.account < Agent2.account and WhoWin == "Poor":
                self.go_GiveMoney(Agent2, Agent1)
            else:
                pass

        return None

    def calc_Gini(self, Account_list):

        x = sorted(Account_list)
        N = len(Account_list)
        B = sum(xi * (N - i) for i, xi in enumerate(x)) / (N * sum(x))

        return (1 + (1 / N) - 2 * B)

    def calc_WealthAndGini(self, AgentList):

        Account_list = []
        for agent in AgentList:
            Account_list.append(agent.account)

        Account_array = np.array(Account_list)
        self.total_wealth = Account_array.sum()
        self.gini = self.calc_Gini(Account_list)

        return None
