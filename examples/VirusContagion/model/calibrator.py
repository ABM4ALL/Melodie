from typing import Union

from Melodie.calibrator import Calibrator
from .environment import CovidEnvironment


class CovidCalibrator(Calibrator):
    def setup(self):
        self.add_scenario_calibrating_property("infection_probability")
        self.add_environment_property("accumulated_infection")

    def distance(self, environment: CovidEnvironment):
        print(
            "infection_rate",
            environment.accumulated_infection / environment.scenario.agent_num,
        )
        return (
            environment.accumulated_infection / environment.scenario.agent_num - 0.75
        ) ** 2

    def target_function(self, env: CovidEnvironment) -> Union[float, int]:
        return self.distance(env)
