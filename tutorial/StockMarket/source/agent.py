from typing import TYPE_CHECKING

from Melodie import Agent
from .order_book import OrderType, Order

if TYPE_CHECKING:
    from .scenario import StockScenario


class StockAgent(Agent):
    scenario: "StockScenario"

    def setup(self):
        self.forecast_rule_id = 0
        self.switch_intensity = 0.0
        self.wealth = 0
        self.wealth_high = 0
        self.wealth_low = 0

    def update_wealth_variation(self):
        self.wealth_high = max(self.wealth_high, self.wealth)
        self.wealth_low = min(self.wealth_low, self.wealth)

    def switch_forecast_rule(self):
        ...
