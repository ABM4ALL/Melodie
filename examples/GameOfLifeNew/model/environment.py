# -*- coding: utf-8 -*-
__author__ = 'Songmin'

import random
from typing import TYPE_CHECKING, List, Tuple

import numpy as np

from Melodie import AgentList, Environment
from Melodie.grid import Grid
from Melodie.network import Network
from .scenario import GameOfLifeScenario

if TYPE_CHECKING:
    from .spot import GameOfLifeSpot


class GameOfLifeEnvironment(Environment):

    def setup(self):
        scenario: GameOfLifeScenario = self.current_scenario()
        self.buffer_status_next_tick: np.ndarray = None

    def step(self, grid: "Grid"):
        if self.buffer_status_next_tick is None:
            self.buffer_status_next_tick = np.zeros((grid.width, grid.height), np.int)
        for x in range(grid.width):
            for y in range(grid.height):
                neighbor_positions = grid.get_neighbors(x, y)
                count = self.count_neighbor_alives(grid, neighbor_positions)
                current_spot: GameOfLifeSpot = grid.get_spot(x, y)
                self.buffer_status_next_tick[y][x] = current_spot.alive_on_next_tick(count)

        for x in range(grid.width):
            for y in range(grid.height):
                spot: GameOfLifeSpot = grid.get_spot(x, y)
                if self.buffer_status_next_tick[y][x] == 0:
                    spot.alive = False
                else:
                    spot.alive = True

    def count_neighbor_alives(self, grid: 'Grid', neighbor_positions: "List[Tuple[int]]"):
        alive_count = 0
        for neighbor_pos in neighbor_positions:
            spot: GameOfLifeSpot = grid.get_spot(neighbor_pos[0], neighbor_pos[1])
            if spot.alive:
                alive_count += 1
        return alive_count
