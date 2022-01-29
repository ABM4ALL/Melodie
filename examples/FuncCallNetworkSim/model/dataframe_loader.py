import pandas as pd

from Melodie import DataFrameLoader


class FuncDataframeLoader(DataFrameLoader):
    def register_scenario_dataframe(self) -> None:
        self.register_dataframe('simulator_scenarios', pd.DataFrame(
            [{"id": i, "reliability": 0.99, "number_of_run": 1, "periods": 100} for i in range(100)]))
