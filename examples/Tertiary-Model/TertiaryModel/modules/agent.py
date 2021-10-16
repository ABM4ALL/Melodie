# -*- coding: utf-8 -*-
__author__ = 'Songmin'

import numpy as np
from Melodie import Agent


class TertiaryAgent(Agent):

    def setup(self):
        self.id = 0
        self.account = 0.0
        self.productivity = 0.0

