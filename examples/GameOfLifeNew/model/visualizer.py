# -*- coding:utf-8 -*-
# @Time: 2021/11/12 18:51
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: visualizer.py
import numba
import numpy as np
from numba import typed

from Melodie.grid import Grid
from Melodie.visualization import GridVisualizer


@numba.njit
def spot_role_jit(spot):
    if spot["alive"]:
        return 1
    else:
        return -1


@numba.njit
def convert_to_1d(height, x, y):
    return x * height + y


@numba.njit
def parse_with_jit(grid) -> np.ndarray:
    grid_roles = np.zeros((grid.height * grid.width, 4))
    for x in range(grid.width):
        for y in range(grid.height):
            spot = grid.get_spot(x, y)
            role = spot_role_jit(spot)

            grid_roles[convert_to_1d(grid.height, x, y), 0] = x
            grid_roles[convert_to_1d(grid.height, x, y), 1] = y
            grid_roles[convert_to_1d(grid.height, x, y), 2] = 0
            grid_roles[convert_to_1d(grid.height, x, y), 3] = role
    return grid_roles


class GameOfLifeVisualizer(GridVisualizer):
    def spot_role(self, spot):
        if spot.alive:
            return 1
        else:
            return -1

    def spot_role_jit(self, spot):
        if spot["alive"]:
            return 1
        else:
            return -1

    def parse(self, grid):
        if isinstance(grid, Grid):
            self.parse_grid_roles(grid, self.spot_role)
        else:
            self.parse_roles_jit(grid)

    def parse_roles_jit(self, grid):
        parsed = parse_with_jit(grid)
        self.grid_roles = parsed.tolist()
