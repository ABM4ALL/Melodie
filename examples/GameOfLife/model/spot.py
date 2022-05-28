# -*- coding:utf-8 -*-

import random

from Melodie import Spot


class GameOfLifeSpot(Spot):
    def setup(self):
        self.alive = random.random() > 0.3
        self.role: int = self.calc_role()


    def calc_role(self):
        return 1 if self.alive else -1

    def update_role(self):
        self.role: int = self.calc_role()

    def alive_on_next_tick(self, surround_alive_count: int) -> bool:
        if self.alive:
            if surround_alive_count == 2 or surround_alive_count == 3:
                return True
            else:
                return False
        else:
            if surround_alive_count == 3:
                return True
            else:
                return False
