from typing import List

from Melodie import Simulator
from .scenario import ShellingModelScenario


class ShellingModelSimulator(Simulator):
    def generate_scenarios(self) -> List['ShellingModelScenario']:
        scenario = ShellingModelScenario(0)
        scenario.periods = 100
        scenario.desired_sametype_neighbors = 4
        return [scenario]
