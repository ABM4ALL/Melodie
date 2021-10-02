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

    def go_money_produce(self, AgentList):

        for agent in AgentList:
            agent.go_produce()

        return None

    def go_give_money(self, agent_from: 'GINIAgent', agent_to: 'GINIAgent'):

        if agent_from.account == 0:
            pass
        else:
            agent_from.account -= 1
            agent_to.account += 1

        return None

    def go_money_transfer(self, agent_list: 'AgentManager'):
        for sub_period in range(0, self.trade_num):
            [agent_1, agent_2] = agent_list.random_sample(2)

            who_win = 0
            rand = np.random.uniform(0, 1)
            if rand <= self.win_prob:
                who_win = "Rich"
            else:
                who_win = "Poor"

            if agent_1.account >= agent_2.account and who_win == "Rich":
                self.go_give_money(agent_2, agent_1)
            elif agent_1.account < agent_2.account and who_win == "Rich":
                self.go_give_money(agent_1, agent_2)
            elif agent_1.account >= agent_2.account and who_win == "Poor":
                self.go_give_money(agent_1, agent_2)
            elif agent_1.account < agent_2.account and who_win == "Poor":
                self.go_give_money(agent_2, agent_1)
            else:
                pass

        return None

    def calc_gini(self, Account_list):

        x = sorted(Account_list)
        N = len(Account_list)
        B = sum(xi * (N - i) for i, xi in enumerate(x)) / (N * sum(x))

        return (1 + (1 / N) - 2 * B)

    def calc_wealth_and_gini(self, AgentList):

        account_list = []
        for agent in AgentList:
            account_list.append(agent.account)

        account_array = np.array(account_list)
        self.total_wealth = account_array.sum()
        self.gini = self.calc_gini(account_list)

        return None