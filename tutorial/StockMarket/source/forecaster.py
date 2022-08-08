from typing import TYPE_CHECKING
import random

import numpy as np

if TYPE_CHECKING:
    from .scenario import StockScenario


class Forecaster:

    def __init__(self, scenario: 'StockScenario'):
        self.scenario = scenario
        # self.fundamentalist_forecast = scenario.fundamentalist_price_benchmark
        # self.chartist_forecast = 0

    def update_chartist_forecast(self, price_series: np.ndarray):
        price_earliest = price_series[0]
        price_latest = price_series[-1]
        length = len(price_series)
        price_change_rate = (price_latest - price_earliest)/(price_earliest * length)
        forecast = price_latest * (1 + price_change_rate * random.uniform(0.9, 1.1))
        self.chartist_forecast = forecast
        return forecast

    def update_fundamentalist_forecast(self):
        forecast = self.scenario.fundamentalist_price_benchmark * random.uniform(0.9, 1.1)
        self.fundamentalist_forecast = forecast
        return forecast

    def get_forecast(self, forecast_rule_id: int) -> int:
        if forecast_rule_id == 0:
            return self.fundamentalist_forecast
        elif forecast_rule_id == 1:
            return self.chartist_forecast
        else:
            raise NotImplementedError(f"Not implemented --> forecast_rule_id = {forecast_rule_id}")



