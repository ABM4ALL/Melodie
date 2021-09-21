# -*- coding: utf-8 -*-
__author__ = 'Songmin'

import numpy as np
from Melodie.agent import  Agent


class GINIAgent(Agent):
    params = ["ID", "Account", "Productivity"]
    types = {
        "ID": "INTEGER",
        "Account": "REAL",
        "Productivity": "REAL"
    }

    def __init__(self):
        super(GINIAgent, self).__init__()
        self.ID = 0
        self.Account = 0.0
        self.Productivity = 0.0


    def go_produce(self):

        rand = np.random.uniform(0, 1)
        if rand <= self.Productivity:
            self.Account += 1
        else:
            pass

        return None
