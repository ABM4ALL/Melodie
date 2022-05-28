# -*- coding:utf-8 -*-
from Melodie import Scenario


class ShellingModelScenario(Scenario):
    def setup(self):
        self.periods = 100
        self.desired_sametype_neighbors = 3
        pass
