import numpy as np

from Melodie.calibrator import Calibrator
from tutorial.StockMarket.source import data_info
from .environment import StockEnvironment


class StockCalibrator(Calibrator):
    def setup(self):
        self.add_scenario_calibrating_property("fundamentalist_weight_max")

    def collect_data(self):
        self.add_environment_property("close")

    def distance(self, environment: "StockEnvironment"):
        std1 = np.std(self.get_dataframe(data_info.calibrator_target.df_name)["close"])
        std2 = np.std(environment.order_book.price_history[:, -1])
        return abs(std1 - std2)
