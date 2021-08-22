# -*- coding: utf-8 -*-
__author__ = 'Songmin'

import random
import numpy as np

from ..Config import GiniScenario


class Environment:

    def __init__(self, scenario: GiniScenario):
        self.TradeNum = scenario.TradeNum
        self.WinProb = scenario.RichWinProb
        self.TotalWealth = 0
        self.Gini = 0

    def go_MoneyProduce(self, AgentList):

        for agent in AgentList:
            agent.go_produce()

        return None

    def go_GiveMoney(self, AgentFrom, AgentTo):

        if AgentFrom.Account == 0:
            pass
        else:
            AgentFrom.Account -= 1
            AgentTo.Account += 1

        return None

    def go_MoneyTransfer(self, AgentList):

        for sub_period in range(0, self.TradeNum):
            [Agent1, Agent2] = random.sample(AgentList, 2)

            WhoWin = 0
            rand = np.random.uniform(0, 1)
            if rand <= self.WinProb:
                WhoWin = "Rich"
            else:
                WhoWin = "Poor"

            if Agent1.Account >= Agent2.Account and WhoWin == "Rich":
                self.go_GiveMoney(Agent2, Agent1)
            elif Agent1.Account < Agent2.Account and WhoWin == "Rich":
                self.go_GiveMoney(Agent1, Agent2)
            elif Agent1.Account >= Agent2.Account and WhoWin == "Poor":
                self.go_GiveMoney(Agent1, Agent2)
            elif Agent1.Account < Agent2.Account and WhoWin == "Poor":
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
            Account_list.append(agent.Account)

        Account_array = np.array(Account_list)
        self.TotalWealth = Account_array.sum()
        self.Gini = self.calc_Gini(Account_list)

        return None
