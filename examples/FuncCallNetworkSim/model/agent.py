# -*- coding: utf-8 -*-
__author__ = 'Songmin'

import random
from Melodie import Agent


class FuncAgent(Agent):
    """
    FuncAgent acts as the node from the
    TODO:Forbid user rewriting id and other reserved properties in setup() function!
    """

    def setup(self):

        self.reliability = 0.99
        self.status = 0  # 0 for normal, 1 for breakdown

    def go_produce(self):

        rand = random.random()
        if rand <= self.productivity:
            self.account += 1
        else:
            pass

        return None
