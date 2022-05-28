# -*- coding:utf-8 -*-
import pandas as pd
from Melodie import DataFrameLoader


class GameOfLifeDataFrameLoader(DataFrameLoader):
    def register_scenario_dataframe(self) -> None:
        self.register_dataframe('simulator_scenarios', pd.DataFrame(
            [{"id": i, "periods": 1000} for i in range(2)]))
