from Melodie import Scenario


class StockScenario(Scenario):
    def setup(self):
        self.period_num = 0
        self.period_ticks = 0
        self.agent_num = 0
        self.fundamentalist_weight_min = 0.0
        self.fundamentalist_weight_max = 0.0
        self.fundamentalist_forecast_min = 0.0
        self.fundamentalist_forecast_max = 0.0
        self.chartist_forecast_start_min = 0.0
        self.chartist_forecast_start_max = 0.0
        self.chartist_forecast_memory_length = 0
        self.stock_price_start = 0.0
        self.stock_trading_volume = 0
        self.stock_account_start = 0
        self.cash_account_start = 0.0


