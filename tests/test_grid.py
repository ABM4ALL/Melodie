# -*- coding:utf-8 -*-
# @Time: 2021/11/11 10:39
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: test_grid.py
import json
import random
import sys
import time
from .config import model
from typing import Union, TYPE_CHECKING

from Melodie import Grid, Spot, GridAgent, Agent, AgentList
import logging

if TYPE_CHECKING:
    from Melodie.boost import JITGrid

logger = logging.getLogger(__name__)

N = 10000_000


def agents(grid: Union['JITGrid', Grid]):
    WOLVES = 0
    SHEEP = 1
    a0 = GridAgent(0, 1, 1)
    a1 = GridAgent(1, 1, 1)
    a2 = GridAgent(2, 1, 1)
    a3 = GridAgent(3, 1, 1)
    type_error_agent = Agent(0)
    grid.add_agent(a0, WOLVES)
    grid.add_agent(a1, WOLVES)
    grid.add_agent(a2, WOLVES)
    grid.add_agent(a3, SHEEP)
    try:
        grid.add_agent(type_error_agent, SHEEP)
        assert False, "An error should be raised at line above"
    except TypeError:
        pass
    # try:
    #     grid.add_agent(a3, 2)
    #     assert False, "An error should be raised at line above"
    # except ValueError:
    #     pass
    grid.remove_agent(a0, WOLVES)
    mammals_at_1_1 = grid.get_agent_ids(1, 1)
    assert (1, WOLVES) in mammals_at_1_1, mammals_at_1_1
    assert (2, WOLVES) in mammals_at_1_1
    assert (3, WOLVES) not in mammals_at_1_1

    assert (3, SHEEP) in mammals_at_1_1

    grid.move_agent(a3, SHEEP, 2, 2)
    assert (3, SHEEP) in grid.get_agent_ids(2, 2)


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


def test_agent_id_mgr():
    from Melodie.boost.grid import AgentIDManager
    am = AgentIDManager(10, 10)
    SHEEP = 0
    WOLF = 1
    am.add_agent(0, 0, 1, 1)  # add a sheep at (1, 1)
    assert 10 * 1 + 1 not in am.get_empty_spots()
    am.remove_agent(0, 0, 1, 1)  # remove a sheep from (1, 1)
    assert 10 * 1 + 1 in am.get_empty_spots()

    am.add_agent(0, 0, 1, 1)  # add a sheep at (1, 1)
    try:
        am.add_agent(0, 0, 1, 1)  # add a sheep at (1, 1)
        assert False, "An Error should be raised above"
    except ValueError:
        pass
    print(len(am.get_empty_spots()))
    am.add_agent(0, WOLF, 1, 1)
    print(am.agents_on_spot(1, 1))
    assert (0, WOLF) in am.agents_on_spot(1, 1)
    assert (0, SHEEP) in am.agents_on_spot(1, 1)
    print(am.agents_on_spot(5, 5))
    pass


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
    grid = Grid(Spot, 100, 100, multi=True)
    grid2 = Grid(Spot, 100, 100, multi=True)

    CATRGORY_A = 0
    CATRGORY_B = 1

    for agent in agents:
        grid2.add_agent(agent, CATRGORY_A)
    for agent in agents_b:
        grid2.add_agent(agent, CATRGORY_B)
    N = 100
    t0 = time.time()
    for i in range(N):
        roles = grid2.get_roles()
    t1 = time.time()

    for i in range(N):
        roles2 = grid2.get_roles()
    t2 = time.time()

    print(t1 - t0, t2 - t1)
    print(roles2[1])


def test_single_grid():
    agents = [GridAgent(i) for i in range(15)]
    grid = Grid(Spot, 4, 4)
    for i in range(4):
        for j in range(4):
            if i * 4 + j < 15:
                agent = agents[i * 4 + j]
                agent.x = i
                agent.y = j
                grid.add_agent(agent, 0)
    spot = grid.find_empty_spot()
    assert spot == (3, 3), spot
    grid.move_agent(agents[0], 0, 3, 3)
    spot = grid.find_empty_spot()
    assert spot == (0, 0), spot


def test_agents_nojit():
    width = 10
    height = 20
    grid = Grid(Spot, width, height)

    agents(grid)
    neighbors(grid)
    convert(grid)


def test_containers():
    grid = Grid(Spot, 10, 10)
    agent_list: AgentList[GridAgent] = model.create_agent_container(GridAgent, 10)
    for i in range(10):
        agent_list[i].x = i
        agent_list[i].y = i
    grid.add_agent_container(0, agent_list)
    agents_on_grid = grid.get_agents(1, 1)
    assert len(agents_on_grid) == 1
    assert agents_on_grid[0].x == 1, agents_on_grid[0].y == 1
