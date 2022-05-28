from typing import List

from Melodie import Simulator
from .scenario import ShellingModelScenario
from .visualizer import ShellingVisualizer


class ShellingModelSimulator(Simulator):
    def generate_scenarios(self) -> List["ShellingModelScenario"]:
        scenario = ShellingModelScenario(0)
        scenario.periods = 100
        scenario.desired_sametype_neighbors = 4
        return [scenario]

    def setup(self):
        self.visualizer = ShellingVisualizer()
        self.visualizer.setup()
