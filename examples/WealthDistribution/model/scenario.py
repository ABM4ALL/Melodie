
from Melodie import Scenario


class GiniScenario(Scenario):
    def setup(self):
        self.periods = 0
        self.agent_num = 0
        self.agent_account_min = 0.0
        self.agent_account_max = 0.0
        self.agent_productivity = 0.0
        self.trade_num = 0
        self.rich_win_prob = 0.0


