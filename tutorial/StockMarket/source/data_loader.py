from typing import TYPE_CHECKING

import numpy as np

from Melodie import DataLoader
from tutorial.CovidContagion.source import data_info

if TYPE_CHECKING:
    from .scenario import StockScenario


class StockDataLoader(DataLoader):
    def setup(self):
        self.load_dataframe(data_info.simulator_scenarios)
        self.generate_dataframe()

    @staticmethod
    def init_vaccination_trust(vaccination_trust_percentage: float):
        vaccination_trust_state = 0
        if np.random.uniform(0, 1) <= vaccination_trust_percentage:
            vaccination_trust_state = 1
        return vaccination_trust_state

    def generate_dataframe(self):

        with self.dataframe_generator(data_info.agent_params.df_name, lambda scenario: scenario.agent_num) as g:
            # 第一个参数改成DataFrameInfo的类型

            def generator_func(scenario: "StockScenario"):
                return {
                    "id": g.increment(),
                    "vaccination_trust_state": self.init_vaccination_trust(scenario.vaccination_trust_percentage),
                }

            g.set_row_generator(generator_func)
            g.set_column_data_types(data_info.agent_params.columns)
