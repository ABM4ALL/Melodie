# -*- coding: utf-8 -*-
__author__ = 'Songmin'

import random
from typing import Optional

from Melodie import Agent


class GiniAgent(Agent):

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
