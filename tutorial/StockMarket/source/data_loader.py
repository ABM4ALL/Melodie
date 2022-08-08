from typing import TYPE_CHECKING

import numpy as np

from Melodie import DataLoader
from tutorial.StockMarket.source import data_info

if TYPE_CHECKING:
    from .scenario import StockScenario


class StockDataLoader(DataLoader):
    def setup(self):
        self.load_dataframe(data_info.simulator_scenarios)
        self.load_dataframe(data_info.id_forecast_rule)
        self.generate_agent_dataframe()

    @staticmethod
    def init_forecast_rule_id(chartist_percentage: float):
        forecast_rule_id = 0
        if np.random.uniform(0, 1) <= chartist_percentage:
            forecast_rule_id = 1
        return forecast_rule_id

    def generate_agent_dataframe(self):

        with self.dataframe_generator(data_info.agent_params, lambda scenario: scenario.agent_num) as g:

            def generator_func(scenario: "StockScenario"):
                return {
                    "id": g.increment(),
                    "forecast_rule_id": self.init_forecast_rule_id(scenario.chartist_percentage_start),
                    "switch_intensity": scenario.switch_intensity,
                    "stock_account": scenario.stock_account_start,
                    "cash_account": scenario.cash_account_start
                }

            g.set_row_generator(generator_func)
