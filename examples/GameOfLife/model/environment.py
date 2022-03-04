# -*- coding: utf-8 -*-
__author__ = 'Songmin'

from typing import TYPE_CHECKING

import numpy as np

from Melodie import Environment
from Melodie.grid import Grid
from .scenario import GameOfLifeScenario

if TYPE_CHECKING:
    from .spot import GameOfLifeSpot


class GameOfLifeEnvironment(Environment):
    scenario: GameOfLifeScenario

    def setup(self):
        pass

    # def choose_strategy(self, al: "AgentList[GameOfLifeSpot]"):
    #     strategy = Strategy(1, al)
    #     if random.random() > 0.5:
    #         return strategy.strategy1()
    #     else:
    #         return strategy.strategy2()

    def step(self, grid: "Grid"):

        buffer_status_next_tick: "np.ndarray" = np.zeros((grid.width(), grid.height()), dtype=np.int64)
        #
        for x in range(grid.width()):
            for y in range(grid.height()):
                neighbor_positions: "np.ndarray" = grid.get_neighbors(x, y)
                count: int = self.count_neighbor_alives(grid, neighbor_positions)
                current_spot: 'GameOfLifeSpot' = grid.get_spot(x, y)
                buffer_status_next_tick[y][x] = current_spot.alive_on_next_tick(count)

        for x in range(grid.width()):
            for y in range(grid.height()):
                spot: 'GameOfLifeSpot' = grid.get_spot(x, y)
                spot.update_role()
                if buffer_status_next_tick[y][x] == 0:
                    spot.alive = False
                else:
                    spot.alive = True

    def count_neighbor_alives(self, grid: 'Grid', neighbor_positions: "np.ndarray"):
        alive_count = 0
        for neighbor_pos in neighbor_positions:
            spot: 'GameOfLifeSpot' = grid.get_spot(neighbor_pos[0], neighbor_pos[1])
            if spot.alive:
                alive_count += 1
        return alive_count
