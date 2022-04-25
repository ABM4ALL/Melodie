# -*- coding:utf-8 -*-
# @Time: 2021/9/21 10:28
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: scenario.py

import random
from typing import TYPE_CHECKING

import numpy as np

from Melodie import Environment, Grid
from .scenario import GameOfLifeScenario

if TYPE_CHECKING:
    from .spot import GameOfLifeSpot


class GameOfLifeEnvironment(Environment):
    scenario: GameOfLifeScenario

    def setup(self):
        self.value1 = 0
        self.value2 = 0

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
        self.value1 = random.random()
        self.value2 = random.random() * 2

    def count_neighbor_alives(self, grid: 'Grid', neighbor_positions: "np.ndarray"):
        alive_count = 0
        for neighbor_pos in neighbor_positions:
            spot: 'GameOfLifeSpot' = grid.get_spot(neighbor_pos[0], neighbor_pos[1])
            if spot.alive:
                alive_count += 1
        return alive_count
