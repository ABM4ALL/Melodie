from typing import List

from Melodie import Scenario


class GameOfLifeScenario(Scenario):
    def setup(self):
        self.periods = 1000
        self.a = 10

    def properties_as_parameters(self) -> List[Scenario.BaseParameter]:
        return [
            Scenario.NumberParameter("periods", self.periods, 50, 300, 1),
            Scenario.NumberParameter("a", self.a, 0, 20, 1),
        ]
