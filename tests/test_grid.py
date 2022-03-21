# -*- coding:utf-8 -*-
# @Time: 2021/11/11 10:39
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: test_grid.py
import json
import random
import sys
import time
from typing import Union, TYPE_CHECKING

import numpy as np

from Melodie import Grid, Spot, GridAgent, Agent

import logging

if TYPE_CHECKING:
    from Melodie.boost import JITGrid

logger = logging.getLogger(__name__)

N = 10000_000


def agents(grid: Union['JITGrid', Grid]):
    grid.add_category('wolves')
    grid.add_category('sheep')
    a0 = GridAgent(0, 1, 1)
    a1 = GridAgent(1, 1, 1)
    a2 = GridAgent(2, 1, 1)
    a3 = GridAgent(3, 1, 1)
    error_agent = Agent(0)
    grid.add_agent(a0, 'wolves')
    grid.add_agent(a1, 'wolves')
    grid.add_agent(a2, 'wolves')
    grid.add_agent(a3, 'sheep')
    try:
        grid.add_agent(error_agent, "sheep")
        assert False, "An error should be raised at line above"
    except TypeError:
        pass
    try:
        grid.add_agent(a3, 'undefined')
        assert False, "An error should be raised at line above"
    except ValueError:
        pass
    grid.remove_agent(a0, 'wolves')
    wolves_at_1_1 = grid.get_agent_ids('wolves', 1, 1)
    assert 1 in wolves_at_1_1
    assert 2 in wolves_at_1_1
    assert 3 not in wolves_at_1_1
    sheep_at_1_1 = grid.get_agent_ids('sheep', 1, 1)
    assert 3 in sheep_at_1_1

    grid.move_agent(a3, 'sheep', 2, 2)
    assert 3 in grid.get_agent_ids('sheep', 2, 2)


def neighbors(grid: Grid):
    px, py = int(grid.width() / 2), int(grid.height() / 2)
    neighbor_ids = grid.get_neighbors(px, py, 1)
    if not isinstance(grid, Grid):  # convert jit data types
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

    x = px
    y = py
    if isinstance(grid, Grid):
        assert x == grid.get_spot(x, y).x
        assert y == grid.get_spot(x, y).y
    else:
        assert x == grid.get_spot(x, y)['x']
        assert y == grid.get_spot(x, y)['y']
    neighbor_ids = grid.get_neighbors(grid.width() - 1, grid.height() - 1, 1)
    grid.get_spot(0, 0)


# def test_agent_list():
#     if JIT_AVAILABLE:
#         from Melodie.boost import JITGrid
#     else:
#         return
#     grid = JITGrid(5, 5)
#     grid.add_category('wolfs')
#     grid.add_category('sheeps')
#
#     al1 = AgentList(Agent, 10, model)
#     al2 = AgentList(Agent, 10, model)
#     grid.add_agent(al1[0].id, 3, 3)
#     grid.add_agent(al1[1].id, 2, 3)
#     grid.add_agent(al1[2].id, 3, 3)
#     grid.add_agent(al1[3].id, 4, 3)
#     grid.add_agent(al2[3].id, 4, 3)
#     print(al2)
#     print(al1)
#     n = grid.get_neighbors(3, 3)
#     print(n)
#     ids = grid.get_agent_ids(4, 3)
#     print(ids)
#     print(grid._agent_categories)

def convert(grid: Union[Grid, 'JITGrid']):
    if isinstance(grid, Grid):
        arr = grid.to_2d_array('id')
        print(arr)
    else:
        arr = grid.get_2d_array()
        print(arr)


# def test_agents_jit():
#     if JIT_AVAILABLE:
#         from Melodie.boost import JITGrid
#     else:
#         return
#     width = 10
#     height = 20
#     jit_grid = JITGrid(width, height, Spot)
#
#     agents(jit_grid)
#     neighbors(jit_grid)
#     convert(jit_grid)

def test_roles():
    agents = [GridAgent(i) for i in range(10)]
    agents_b = [GridAgent(i) for i in range(10)]
    grid = Grid(Spot, 100, 100)
    grid2 = Grid(Spot, 100, 100)

    grid2.add_category('a')
    grid2.add_category('b')
    for agent in agents:
        grid2.add_agent(agent, 'a')
    for agent in agents_b:
        grid2.add_agent(agent, 'b')
    N = 100
    t0 = time.time()
    for i in range(N):
        roles = grid.get_roles()
    t1 = time.time()

    for i in range(N):
        roles2 = grid2.get_roles()
    t2 = time.time()

    print(t1 - t0, t2 - t1)
    print(roles2[1])


def test_agents_nojit():
    width = 10
    height = 20
    grid = Grid(Spot, width, height)

    agents(grid)
    neighbors(grid)
    convert(grid)
