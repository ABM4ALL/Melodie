import random
import numpy as np
from typing import Type, TYPE_CHECKING

from Melodie import Agent

if TYPE_CHECKING:
    from .scenario import RPSScenario

class RPSAgent(Agent):
    scenario: 'RPSScenario'

    # 石头剪子布
    # 每个period随机抽取多对两个agent，类似于wealth distribution的例子
    # 因为agent的utility function不同，即不同获胜方式的受益、损失不同，策略也应该不用，用individual-learning
    # 看演化出来的行为是不是也不一样，是不是跟博弈均衡一样

    def setup(self):
        self.technology = 0.0
        self.aspiration_level = 0.0
        self.aspiration_update_strategy = 0
        self.historical_aspiration_update_param = 0.0
        self.social_aspiration_update_param = 0.0
        self.profit = 0.0
        self.account = 0.0
        self.profit_aspiration_difference = 0.0
        self.strategy_param_1 = 0.0
        self.strategy_param_2 = 0.0
        self.strategy_param_3 = 0.0
        self.sleep_count = 0
        self.exploration_count = 0
        self.exploitation_count = 0
        self.imitation_count = 0
        self.be_learned_count = 0

    def post_setup(self):
        weight_sum = sum([self.strategy_param_1, self.strategy_param_2, self.strategy_param_3])
        if weight_sum == 0: weight_sum = 1
        self.prob_exploration = self.strategy_param_1 / weight_sum
        self.prob_exploitation = self.strategy_param_2 / weight_sum

    def aspiration_update_historical_strategy(self):
        self.aspiration_level = self.historical_aspiration_update_param * self.profit + \
                                (1 - self.historical_aspiration_update_param) * self.aspiration_level

    def aspiration_update_social_strategy(self, average_profit):
        self.aspiration_level = average_profit

    def technology_search_sleep_strategy(self):
        self.sleep_count += 1

    def technology_search_exploration_strategy(self):
        self.exploration_count += 1
        mean = self.scenario.sigma_exploration
        sigma = self.scenario.sigma_exploration
        technology_search_result = np.random.lognormal(mean, sigma)
        self.technology = max(self.technology, technology_search_result)
        self.account -= self.scenario.cost_exploration

    def technology_search_exploitation_strategy(self):
        self.exploitation_count += 1
        sigma = self.scenario.sigma_exploitation
        technology_search_result = np.random.normal(self.technology, sigma)
        self.technology = max(self.technology, technology_search_result)
        self.account -= self.scenario.cost_exploitation

    def technology_search_imitation_strategy(self, agent_to_learn: 'RPSAgent', technology_search_result: float):
        # the logic is written in the AspirationEnvironment class
        pass







