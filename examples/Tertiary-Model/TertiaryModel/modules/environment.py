# -*- coding: utf-8 -*-
__author__ = 'Songmin'

import random
from typing import TYPE_CHECKING

from Melodie import AgentManager, Environment, current_scenario
from ..model.scenario import TertiaryScenario

if TYPE_CHECKING:
    from .agent import GINIAgent


class TertiaryEnvironment(Environment):

    def setup(self):
        scenario: TertiaryScenario = current_scenario()
        self.trade_num = scenario.trade_num
        self.win_prob = scenario.rich_win_prob
        self.total_wealth = 0
        self.gini = 0

