from Melodie import Scenario


class StockScenario(Scenario):
    def setup(self):
        self.periods = 0
        self.period_ticks = 0
        self.agent_num = 0
        self.chartist_percentage_start = 0.0
        self.chartist_memory_length = 0
        self.fundamentalist_price_benchmark = 0
        self.forecast_rule_evaluation_memory = 0
        self.switch_intensity = 0.0
        self.stock_price_start = 0
        self.stock_trading_volume = 0
        self.stock_account_start = 0
        self.cash_account_start = 0


