from typing import TYPE_CHECKING

import numpy as np

from Melodie import Environment
from .order_book import OrderBook

if TYPE_CHECKING:
    from Melodie import AgentList
    from .agent import StockAgent
    from .scenario import StockScenario


class StockEnvironment(Environment):
    scenario: "StockScenario"

    def setup(self):
        self.order_book = OrderBook(self.scenario)
        self.open = 0.0
        self.high = 0.0
        self.low = 0.0
        self.mean = 0.0
        self.close = 0.0
        self.volume = 0.0

    def agents_update_wealth(self, agents: "AgentList[StockAgent]", period: int):
        price = self.order_book.get_period_close_price(period)
        for agent in agents:
            agent.update_wealth(period, price)

    def agents_update_forecast(self, agents: "AgentList[StockAgent]", period: int):
        memory_length = self.scenario.chartist_forecast_memory_length
        price_series = self.order_book.get_memorized_close_price_series(
            period, memory_length
        )
        for agent in agents:
            agent.update_chartist_forecast(price_series)

    def record_period_trading_info(self, period: int):
        prices = self.order_book.price_history[period]
        volumes = self.order_book.volume_history[period]
        self.open = prices[0]
        self.high = np.max(prices)
        self.low = np.min(prices)
        self.mean = np.mean(prices)
        self.close = prices[-1]
        self.volume = np.sum(volumes)

    @property
    def fundamentalist_weight_max(self):
        return self.scenario.fundamentalist_weight_max
