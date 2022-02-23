
import random

from Melodie import Agent
from .scenario import GiniScenario


class GiniAgent(Agent):
    scenario: GiniScenario

    def setup(self):
        self.account = .0
        self.productivity = .0

    def go_produce(self):
        rand = random.random()
        if rand <= self.productivity:
            self.account += 1
        else:
            pass

        return None
