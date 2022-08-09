import random
from typing import TYPE_CHECKING

import math
import numpy as np

from Melodie import Agent
from .order_book import OrderType, Order

if TYPE_CHECKING:
    from .scenario import StockScenario
    from .environment import StockEnvironment


class StockAgent(Agent):
    scenario: "StockScenario"

    def setup(self):
        self.fundamentalist_weight = 0.0
        self.fundamentalist_forecast = 0.0
        self.chartist_forecast = 0.0
        self.stock_account = 0
        self.cash_account = 0.0
        self.wealth_period = 0.0
        self.wealth = np.zeros((self.scenario.periods, ))

    def update_wealth(self, period: int, period_close_price: float):
        self.wealth_period = self.cash_account + self.stock_account * period_close_price
        self.wealth[period] = self.wealth_period

    def update_chartist_forecast(self, memorized_close_price_series: np.ndarray):
        price_earliest = memorized_close_price_series[0]
        price_latest = memorized_close_price_series[-1]
        length = len(memorized_close_price_series)
        price_change_rate = (price_latest - price_earliest) / (price_earliest * length)
        self.chartist_forecast = price_latest * (1 + price_change_rate)

    @property
    def forecast(self):
        forecast = self.fundamentalist_weight * self.fundamentalist_forecast + \
                   (1 - self.fundamentalist_weight) * self.chartist_forecast
        return forecast

    def create_order(self, current_price: float) -> "Order":
        order = Order(agent_id=self.id)
        if self.forecast >= current_price:
            order.type = OrderType.BID
            order.price = random.uniform(current_price, self.forecast)
            order.volume = self.scenario.stock_trading_volume
        else:
            order.type = OrderType.ASK
            order.price = random.uniform(self.forecast, current_price)
            order.volume = self.scenario.stock_trading_volume
        return order


