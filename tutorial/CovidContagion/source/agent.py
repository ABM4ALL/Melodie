import random
from typing import TYPE_CHECKING

from Melodie import Agent

if TYPE_CHECKING:
    from .scenario import CovidScenario


class CovidAgent(Agent):
    scenario: "CovidScenario"

    def setup(self):
        self.age_group = 0
        self.health_state = 0

    def infection(self, infection_prob: float):
        if random.uniform(0, 1) <= infection_prob:
            self.health_state = 1

    def health_state_transition(self):
        if self.health_state == 1:
            (
                prob_s1_s1,
                prob_s1_s2,
                prob_s1_s3,
            ) = self.scenario.get_state_transition_prob(self.age_group)
            rand = random.uniform(0, 1)
            if rand <= prob_s1_s1:
                pass
            elif prob_s1_s1 < rand <= prob_s1_s1 + prob_s1_s2:
                self.health_state = 2
            else:
                self.health_state = 3
