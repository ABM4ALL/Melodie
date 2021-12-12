import random
import numpy as np
from typing import Type

from Melodie import Agent
from .aspiration_update_strategy import AspirationUpdateStrategy, \
    HistoricalAspirationUpdateStrategy, SocialAspirationUpdateStrategy
from .technology_search_strategy import TechnologySearchStrategy, \
    SleepTechnologySearchStrategy, ExploitationTechnologySearchStrategy, \
    ExplorationTechnologySearchStrategy, ImitationTechnologySearchStrategy


class AspirationAgent(Agent):

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

    def post_setup(self):
        weight_sum = np.array([self.strategy_param_1, self.strategy_param_2, self.strategy_param_3]).sum()

        self.prob_exploitation = self.strategy_param_1 / weight_sum
        self.prob_exploration = self.strategy_param_2 / weight_sum

    def aspiration_update_strategy_choice(self) -> Type[AspirationUpdateStrategy]:
        if self.aspiration_update_strategy == 0:
            return HistoricalAspirationUpdateStrategy
        else:
            return SocialAspirationUpdateStrategy

    def technology_search_strategy_choice(self) -> Type[TechnologySearchStrategy]:
        if self.profit_aspiration_difference >= 0:
            return SleepTechnologySearchStrategy
        else:
            rand = np.random.uniform(0, 1)
            if rand <= self.prob_exploitation:
                return ExploitationTechnologySearchStrategy
            elif self.prob_exploitation < rand <= self.prob_exploitation + self.prob_exploration:
                return ExplorationTechnologySearchStrategy
            else:
                return ImitationTechnologySearchStrategy
