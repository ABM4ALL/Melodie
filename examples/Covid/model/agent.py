import random
import numpy as np
from typing import Type

from Melodie import Agent


class CovidAgent(Agent):

    def setup(self):
        self.x_pos = 0
        self.y_pos = 0
        self.condition = 0

    def move(self):
        self.x_pos = max(0, self.x_pos + random.randint(-1, 1))
        self.y_pos = max(0, self.y_pos + random.randint(-1, 1))







