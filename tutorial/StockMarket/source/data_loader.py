import random
from typing import TYPE_CHECKING

from Melodie import DataLoader
from tutorial.StockMarket.source import data_info

if TYPE_CHECKING:
    from .scenario import StockScenario


class StockDataLoader(DataLoader):
    def setup(self):
        self.load_dataframe(data_info.simulator_scenarios)
        self.generate_agent_dataframe()

    @staticmethod
    def init_fundamentalist_weight(scenario: "StockScenario"):
        weight_min = scenario.fundamentalist_weight_min
        weight_max = scenario.fundamentalist_weight_max
        return random.uniform(weight_min, weight_max)

    @staticmethod
    def init_fundamentalist_forecast(scenario: "StockScenario"):
        forecast_min = scenario.fundamentalist_forecast_min
        forecast_max = scenario.fundamentalist_forecast_max
        return random.uniform(forecast_min, forecast_max)

    @staticmethod
    def init_chartist_forecast(scenario: "StockScenario"):
        forecast_min = scenario.chartist_forecast_start_min
        forecast_max = scenario.chartist_forecast_start_max
        return random.uniform(forecast_min, forecast_max)

    def generate_agent_dataframe(self):

        with self.dataframe_generator(data_info.agent_params, lambda scenario: scenario.agent_num) as g:

            def generator_func(scenario: "StockScenario"):
                return {
                    "id": g.increment(),
                    "fundamentalist_weight": self.init_fundamentalist_weight(scenario),
                    "fundamentalist_forecast": self.init_fundamentalist_forecast(scenario),
                    "chartist_forecast": self.init_chartist_forecast(scenario),
                    "stock_account": scenario.stock_account_start,
                    "cash_account": scenario.cash_account_start
                }

            g.set_row_generator(generator_func)
