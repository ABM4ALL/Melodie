import math
import random
from typing import TYPE_CHECKING

from Melodie import Agent
from .order_book import OrderType, Order, OrderBook

if TYPE_CHECKING:
    from .scenario import StockScenario
    from .forecaster import Forecaster


class StockAgent(Agent):
    scenario: "StockScenario"

    def setup(self):
        self.forecast_rule_id = 0
        self.switch_intensity = 0.0
        self.stock_account = 0
        self.cash_account = 0
        self.wealth = 0
        self.wealth_high = 0
        self.wealth_low = 0

    def update_wealth_variation(self, current_stock_price: int):
        self.wealth = self.cash_account + self.stock_account * current_stock_price
        self.wealth_high = max(self.wealth_high, self.wealth)
        self.wealth_low = min(self.wealth_low, self.wealth)

    def create_order(self, forecaster: 'Forecaster', latest_price: int) -> 'Order':
        order = Order(self.id)
        forecast = forecaster.get_forecast(self.forecast_rule_id)
        # print(f'agent {self.id} --> forecast_rule_id = {self.forecast_rule_id}, forecast = {forecast}')
        if forecast >= latest_price:
            order.type = OrderType.BID
            order.price = random.randint(latest_price, forecast)
            order.volume = self.scenario.stock_trading_volume
        else:
            order.type = OrderType.ASK
            order.price = random.randint(forecast, latest_price)
            order.volume = self.scenario.stock_trading_volume
        return order

    def update_forecast_rule(self, fundamentalist_deviation: int, chartist_deviation: int):
        uf = chartist_deviation / (fundamentalist_deviation + chartist_deviation)
        uc = 1 - uf
        beta = self.switch_intensity
        fundamentalist_prob = math.exp(beta * uf) / math.exp(beta * uf) + math.exp(beta * uc)
        rand = random.uniform(0, 1)
        if rand <= fundamentalist_prob:
            self.forecast_rule_id = 0
        else:
            self.forecast_rule_id = 1

