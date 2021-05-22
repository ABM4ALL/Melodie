# -*- coding: utf-8 -*-
__author__ = 'Songmin'

import numpy as np

class Agent:

    def __init__(self, para_series):
        self.ID = para_series["ID_Agent"]
        self.Account = para_series["InitialAccount"]
        self.Productivity = para_series["Productivity"]

    def go_produce(self):

        rand = np.random.uniform(0, 1)
        if rand <= self.Productivity:
            self.Account += 1
        else:
            pass

        return None
