from Melodie import Scenario


class StockScenario(Scenario):
    def setup(self):
        self.periods = 0
        self.period_ticks = 0
        self.agent_num = 0
        self.chartist_percentage = 0.0
        self.chartist_memory_length = 0
        self.fundamentalist_price_benchmark = 0
        self.switch_intensity = 0.0
        self.stock_start_price = 0


