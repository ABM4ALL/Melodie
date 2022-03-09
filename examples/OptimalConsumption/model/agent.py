
import random
import numpy as np
from typing import Type, TYPE_CHECKING

from Melodie import Agent

if TYPE_CHECKING:
    from .scenario import OCScenario


class OCAgent(Agent):
    scenario: 'OCScenario'

    def setup(self):
        self.payoff_rock_win = 0.0
        self.payoff_rock_lose = 0.0
        self.payoff_paper_win = 0.0
        self.payoff_paper_lose = 0.0
        self.payoff_scissors_win = 0.0
        self.payoff_scissors_lose = 0.0
        self.payoff_tie = 0.0
        self.strategy_param_1 = 0.0
        self.strategy_param_2 = 0.0
        self.strategy_param_3 = 0.0
        self.period_competitor_id = 0
        self.period_action = 0 # rock = 0, paper = 1, scissors = 2
        self.period_payoff = 0.0
        self.total_payoff = 0.0
        self.rock_count = 0
        self.paper_count = 0
        self.scissors_count = 0

    def setup_action_probability(self):
        weight_sum = np.array([self.strategy_param_1, self.strategy_param_2, self.strategy_param_3]).sum()
        if weight_sum == 0: weight_sum = 1
        self.prob_rock = self.strategy_param_1 / weight_sum
        self.prob_paper = self.strategy_param_2 / weight_sum

    def action_choice(self):
        rand = np.random.uniform(0, 1)
        if rand <= self.prob_rock:
            action = 0
            self.rock_count += 1
        elif self.prob_rock < rand <= self.prob_rock + self.prob_paper:
            action = 1
            self.paper_count += 1
        else:
            action = 2
            self.scissors_count += 1
        self.period_action = action
        return action

    def update_account_tie(self):
        self.period_payoff = self.payoff_tie
        self.total_payoff += self.payoff_tie

    def update_account_win(self):
        if self.period_action == 0:
            self.period_payoff = self.payoff_rock_win
            self.total_payoff += self.payoff_rock_win
        elif self.period_action == 1:
            self.period_payoff = self.payoff_paper_win
            self.total_payoff += self.payoff_paper_win
        elif self.period_action == 2:
            self.period_payoff = self.payoff_scissors_win
            self.total_payoff += self.payoff_scissors_win

    def update_account_lose(self):
        if self.period_action == 0:
            self.period_payoff = self.payoff_rock_lose
            self.total_payoff += self.payoff_rock_lose
        elif self.period_action == 1:
            self.period_payoff = self.payoff_paper_lose
            self.total_payoff += self.payoff_paper_lose
        elif self.period_action == 2:
            self.period_payoff = self.payoff_scissors_lose
            self.total_payoff += self.payoff_scissors_lose






