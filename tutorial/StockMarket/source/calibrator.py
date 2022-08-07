from typing import Union

from Melodie.calibrator import Calibrator
from .environment import StockEnvironment


class StockCalibrator(Calibrator):
    def setup(self):
        self.add_environment_calibrating_property("infection_probability")
        self.add_environment_result_property("accumulated_infection")

    def distance(self, environment: 'StockEnvironment'):
        # distance =
        # return distance
        ...

    def target_function(self, env: 'StockEnvironment') -> Union[float, int]:
        # return self.distance(env)
        ...
