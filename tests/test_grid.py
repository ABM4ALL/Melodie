# -*- coding:utf-8 -*-
# @Time: 2021/11/11 10:39
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: test_grid.py
import json
import random
import sys
import time

import numba
import numpy as np

from Melodie.grid import Grid, Spot, build_jit_class
import logging
logger = logging.getLogger(__name__)

N = 10000_000


def routine(grid, width, height):
    x = random.randint(0, width - 1)
    y = random.randint(0, height - 1)
    print(x, y)
    # try:
    #     grid.add_agent(0, width, 0)  # boundary check
    #
    # except IndexError:
    #     pass
    # try:
    #     grid.remove_agent(0, 0, height)  # boundary check
    # except IndexError:
    #     pass

    grid.add_agent(0, x, y)
    grid.add_agent(1, x, y)
    try:
        grid.add_agent(1, x, y)
        raise Exception("The former line should raise ValueError.")
    except ValueError:
        pass
    agent_ids = grid.get_agent_ids(x, y)
    assert 1 in agent_ids
    grid.remove_agent(1, x, y, )
    agent_ids = grid.get_agent_ids(x, y)
    assert 0 in agent_ids
    assert 1 not in agent_ids
    try:
        grid.remove_agent(3, x, y)
    except ValueError:
        pass
    target_x = random.randint(0, width - 1)
    target_y = random.randint(0, height - 1)
    grid.move_agent(0, x, y, target_x, target_y)
    assert 0 in grid.get_agent_ids(target_x, target_y)
    if isinstance(grid, Grid):
        assert x == grid.get_spot(x, y).x
        assert y == grid.get_spot(x, y).y
    else:
        assert x == grid.get_spot(x, y)['x']
        assert y == grid.get_spot(x, y)['y']


def neighbors(grid):
    px, py = int(grid.width / 2), int(grid.height / 2)
    neighbor_ids = grid.get_neighbors(px, py, 1)
    if not isinstance(grid, Grid):
        print(neighbor_ids)
        l = [(neighbor_ids[i][0], neighbor_ids[i][1]) for i in range(neighbor_ids.shape[0])]
        print(l)
        neighbor_ids = set(l)
    else:
        neighbor_ids = set([(neighbor_ids[i][0], neighbor_ids[i][1]) for i in range(len(neighbor_ids))])

    assert len(list(neighbor_ids)) == 8

    # When comparing tuples, python compares the value item by item.
    assert (px - 1, py) in neighbor_ids
    assert (px + 1, py) in neighbor_ids
    assert (px + 1, py + 1) in neighbor_ids
    assert (px + 1, py - 1) in neighbor_ids


def test_to_json():
    g = Grid(Spot, 100, 100)
    t0 = time.time()
    l = []
    for x in range(g.width):
        for y in range(g.height):
            l.append(g.get_spot(x, y).__dict__)
    t1 = time.time()
    s = json.dumps(l)
    t2 = time.time()
    print(t2 - t0, t2 - t1, sys.getsizeof(s))


def test_agents():
    width = 10
    height = 20
    grid = Grid(Spot, width, height)
    jit_grid = build_jit_class(width, height)
    try:
        routine(grid, width, height)
        neighbors(grid)
    except:
        raise Exception(f"Test failed for locals: {locals()}")

    try:
        routine(jit_grid, width, height)
        neighbors(jit_grid)
    except:
        raise Exception(f"Test failed for locals: {locals()}")
