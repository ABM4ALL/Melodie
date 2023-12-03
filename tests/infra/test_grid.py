# -*- coding:utf-8 -*-
import logging
from typing import Union

import numpy as np

from Melodie import Grid, Spot, GridAgent, Agent, AgentList
from tests.infra.config import model

logger = logging.getLogger(__name__)

N = 10000_000


class TestGridAgent(GridAgent):
    def set_category(self):
        self.category = 0


class Wolf(GridAgent):
    def set_category(self):
        self.category = 0


class Sheep(GridAgent):
    def set_category(self):
        self.category = 1


def agents(grid: Union[Grid]):
    WOLVES = 0
    SHEEP = 1
    a0 = Wolf(0, 1, 1)
    a1 = Wolf(1, 1, 1)
    a2 = Wolf(2, 1, 1)
    a3 = Sheep(3, 1, 1)
    type_error_agent = Agent(0)
    grid.add_agent(a0)
    grid.add_agent(a1)
    grid.add_agent(a2)
    grid.add_agent(a3)

    try:
        grid.add_agent(type_error_agent)
        assert False, "An error should be raised at line above"
    except TypeError:
        pass
    # try:
    #     grid.add_agent(a3, 2)
    #     assert False, "An error should be raised at line above"
    # except ValueError:
    #     pass
    grid.remove_agent(a0)

    mammals_at_1_1 = grid.get_spot_agents(grid.get_spot(1, 1))
    print("adasdadasdasdasdsa", mammals_at_1_1)
    assert (WOLVES, 1) in mammals_at_1_1, mammals_at_1_1

    assert (WOLVES, 2) in mammals_at_1_1
    assert (WOLVES, 3) not in mammals_at_1_1

    assert (SHEEP, 3) in mammals_at_1_1

    grid.move_agent(a3, 2, 2)
    assert (SHEEP, 3) in grid.get_spot_agents(grid.get_spot(2, 2))


def neighbors(grid: Grid):
    px, py = int(grid.width() / 2), int(grid.height() / 2)
    neighbor_ids = grid._get_neighbor_positions(px, py, 1)

    neighbor_ids = set(
        [(neighbor_ids[i][0], neighbor_ids[i][1]) for i in range(len(neighbor_ids))]
    )

    assert len(list(neighbor_ids)) == 8

    # When comparing tuples, python compares the value item by item.
    assert (px - 1, py) in neighbor_ids
    assert (px + 1, py) in neighbor_ids
    assert (px + 1, py + 1) in neighbor_ids
    assert (px + 1, py - 1) in neighbor_ids

    x = px
    y = py
    assert x == grid.get_spot(x, y).x
    assert y == grid.get_spot(x, y).y

    neighbor_ids = grid._get_neighbor_positions(grid.width() - 1, grid.height() - 1, 1)
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
#     n = grid._get_neighbor_positions(3, 3)
#     print(n)
#     ids = grid.get_spot_agents(4, 3)
#     print(ids)
#     print(grid._agent_categories)


def convert(grid: Union[Grid]):
    arr = grid.to_2d_array("id")
    print(arr)


CATRGORY_A = 0
CATRGORY_B = 1


def test_roles():
    print("testing roles")

    class GridForRoles(Grid):
        def config_grid(self):
            self.set_size(5, 5)
            self.set_multi(True)

    agents = [TestGridAgent(i) for i in range(10)]
    grid2 = GridForRoles(Spot)
    grid2.setup_params(5, 5, multi=True)
    for agent in agents:
        grid2.add_agent(agent)

    # for i in range(N):
    roles = grid2.get_colormap()

    print(roles)


def test_single_grid():
    print("testing single grid")

    class GridForTest(Grid):
        pass

    agents = [TestGridAgent(i) for i in range(15)]

    grid = GridForTest(
        Spot,
    )
    grid.setup_params(4, 4)
    empty_count = 16
    for i in range(4):
        for j in range(4):
            if i * 4 + j < 15:
                agent = agents[i * 4 + j]
                agent.x = i
                agent.y = j
                grid.add_agent(agent)
                empty_count -= 1

                assert len(grid.get_empty_spots()) == empty_count
    spot = grid.find_empty_spot()
    assert spot == (3, 3), spot
    grid.move_agent(agents[0], 3, 3)
    spot = grid.find_empty_spot()
    assert spot == (0, 0), spot
    es = grid.get_empty_spots()
    assert len(es) == 1
    assert spot in es

    neighbors = grid.get_neighbors(TestGridAgent(100, 2, 2))
    assert len(neighbors) == 8
    nbhd = grid.get_spot_neighborhood(grid.get_spot(2, 2))
    assert len(nbhd) == 8 and isinstance(nbhd, list)

    nbhd = grid.get_agent_neighborhood(TestGridAgent(100, 2, 2))
    assert len(nbhd) == 8 and isinstance(nbhd, list)


def test_agents_nojit():
    print("testing agents nojit")
    width = 10
    height = 20

    class Grid3(Grid):
        pass

    grid = Grid3(Spot)
    grid.setup_params(width, height)
    agents(grid)
    neighbors(grid)
    # convert(grid)


class Grid2(Grid):
    pass


def test_containers():
    print("testing containers")
    grid = Grid2(Spot)
    print("grid created!")
    grid.setup_params(10, 10)
    print("params setup!")
    agent_list: AgentList[TestGridAgent] = model.create_agent_container(
        TestGridAgent, 10
    )
    print(217)
    agent_list.setup_agents(10)
    print("setup!")
    for i in range(10):
        agent_list[i].x = i
        agent_list[i].y = i
        agent_list[i].category = 0
    grid.setup_agent_locations(agent_list, "direct")
    agents_on_grid = grid.get_spot_agents(grid.get_spot(1, 1))
    assert len(agents_on_grid) == 1
    a = agent_list.get_agent(agents_on_grid[0][1])
    assert a.x == 1, a.y == 1
    print("finished!")


def test_roles_2():
    print("testing roles_2")

    class MySpot(Spot):
        def setup(self):
            self.a = 123
            self.b = 123.0

    class GridForRoles(Grid):
        pass

    # agents = [TestGridAgent(i) for i in range(10)]
    # agents_b = [TestGridAgent(i) for i in range(10)]
    grid = GridForRoles(MySpot)
    grid.setup_params(100, 100, multi=True)
    grid.set_spot_property(
        "a",
        np.ones(
            (
                100,
                100,
            ),
            dtype=np.int64,
        )
        * 100,
    )
    spot = grid.get_spot(1, 1)
    print(spot)
    try:
        grid.set_spot_property(
            "a",
            np.ones(
                (
                    100,
                    10,
                ),
                dtype=np.int64,
            )
            * 100,
        )
        assert False
    except AssertionError as e:
        assert "width" in str(e)

    try:
        grid.set_spot_property(
            "a",
            np.ones(
                (
                    10,
                    100,
                ),
                dtype=np.int64,
            )
            * 100,
        )
        assert False
    except AssertionError as e:
        assert "height" in str(e)

    try:
        grid.set_spot_property(
            "a",
            np.ones(
                (10, 100, 1),
                dtype=np.int64,
            )
            * 100,
        )
        assert False
    except AssertionError as e:
        assert "2-dimensional" in str(e)
