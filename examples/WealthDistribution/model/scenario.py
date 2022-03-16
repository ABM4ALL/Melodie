from typing import List

from Melodie import Scenario


class GiniScenario(Scenario):
    def setup(self):
        self.periods = 100
        self.agent_num = 0
        self.agent_account_min = 0.0
        self.agent_account_max = 0.0
        self.agent_productivity = 0.0
        self.trade_num = 0
        self.rich_win_prob = 0.0

        self.add_interactive_parameters([
            self.NumberParameter('agent_productivity', self.agent_productivity, 0.5, 1.5, 0.1),
            self.NumberParameter('rich_win_prob', self.rich_win_prob, 0.1, 1, 0.1)
        ])
