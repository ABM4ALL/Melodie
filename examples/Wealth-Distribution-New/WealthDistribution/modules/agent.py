# -*- coding: utf-8 -*-
__author__ = 'Songmin'

import numpy as np
from Melodie import Agent


class GINIAgent(Agent):

    def setup(self):
        self.id = 0
        self.account = 0.0
        self.productivity = 0.0

    def go_produce(self):

        rand = np.random.uniform(0, 1)
        if rand <= self.productivity:
            self.account += 1
        else:
            pass

        return None
