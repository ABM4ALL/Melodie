from Melodie import Scenario


class AspirationScenario(Scenario):

    def setup(self):
        self.periods = 100
        self.agent_num = 50
        self.market_strategy = 0
        self.market_profit_mean = 1
        self.market_profit_sigma = 0.5
        self.aspiration_update_strategy = 1
        self.historical_aspiration_update_param = 0.5
        self.social_aspiration_update_param = 1.0
        self.initial_technology = 1.0
        self.mean_exploration = 0
        self.sigma_exploration = 0.8
        self.cost_exploration = 2.0
        self.sigma_exploitation = 0.1
        self.cost_exploitation = 1.0
        self.imitation_share = 0.1
        self.imitation_fail_rate = 0.9
        self.cost_imitation = 3.0
