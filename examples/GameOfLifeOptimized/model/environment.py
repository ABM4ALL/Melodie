# cython:language_level=3
# cython: profile=False
# -*- coding: utf-8 -*-
__author__ = 'Songmin'

import random
import cython
import numpy as np

from .scenario import GameOfLifeScenario
from cython.cimports.Melodie.boost.grid import Spot, Grid
from cython.cimports.Melodie.boost.basics import Environment


@cython.cclass
class GameOfLifeSpot(Spot):
    alive = cython.declare(cython.long, visibility='public')
    alive_next = cython.declare(cython.long, visibility='public')
    role = cython.declare(cython.long, visibility='public')

    def setup(self):
        self.alive = random.random() > 0.5
        self.alive_next = self.alive
        self.role: int = self.calc_role()

    @cython.cfunc
    @cython.returns(cython.long)
    def calc_role(self):
        return 1 if self.alive else -1

    @cython.cfunc
    @cython.returns(cython.void)
    def update_role(self):
        self.role: int = self.calc_role()

    @cython.cfunc
    @cython.locals(surround_alive_count=cython.long)
    @cython.returns(cython.bint)
    def alive_on_next_tick(self, surround_alive_count) -> bool:
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


@cython.cclass
class GameOfLifeEnvironment(Environment):
    scenario: GameOfLifeScenario

    def setup(self):
        pass

    @cython.ccall
    @cython.locals(x=cython.long, y=cython.long, current_spot=GameOfLifeSpot, spot=GameOfLifeSpot,
                   neighbor_positions=cython.list)
    def step(self, grid: "Grid"):

        for x in range(grid.width()):
            for y in range(grid.height()):
                neighbor_positions: "list" = grid.get_neighbors(x, y)
                count: cython.long = self.count_neighbor_alives(grid, neighbor_positions)
                current_spot: 'GameOfLifeSpot' = grid.get_spot(x, y)
                current_spot.alive_next = current_spot.alive_on_next_tick(count)

        for x in range(grid.width()):
            for y in range(grid.height()):
                spot: 'GameOfLifeSpot' = grid.get_spot(x, y)
                spot.update_role()
                spot.alive = spot.alive_next

    @cython.cfunc
    @cython.locals(spot=GameOfLifeSpot, alive_count=cython.long, neighbor_positions=cython.list,
                   neighbor_pos=cython.tuple)  # , length=cython.long)
    @cython.returns(cython.long)
    @cython.boundscheck(False)
    def count_neighbor_alives(self, grid: 'Grid', neighbor_positions: "np.ndarray"):
        alive_count = 0
        for neighbor_pos in neighbor_positions:
            spot: 'GameOfLifeSpot' = grid.get_spot(neighbor_pos[0], neighbor_pos[1])
            if spot.alive:
                alive_count += 1
        return alive_count
