from Melodie import Scenario


class OCScenario(Scenario):

    def setup(self):
        self.periods = 0
        self.agent_num = 0
        self.payoff_win_min = 0.0
        self.payoff_win_max = 0.0
        self.payoff_lose_min = 0.0
        self.payoff_lose_max = 0.0
        self.payoff_tie = 0.0



