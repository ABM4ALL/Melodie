# -*- coding: utf-8 -*-
__author__ = 'Songmin'

from Main._Config.ExPackages import *

class Agent:

    def __init__(self, _ParaSeries):
        self.ID = _ParaSeries["ID"]
        self.Account = _ParaSeries["InitialAccount"]
        self.Productivity = _ParaSeries["Productivity"]

    def go_produce(self):

        rand = np.random.uniform(0, 1)
        if rand <= self.Productivity:
            self.Account += 1
        else:
            pass

        return None
