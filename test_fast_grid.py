import sys
import os
import time
# sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from Melodie import Agent, Grid, Spot, AgentList
from Melodie.boost.grid import Grid as FastGrid
from Melodie.boost.agent_list import AgentList as FastAgentList

class NewAgent(Agent):
    def setup(self):
        self.a = 123
        self.b = 456
class FakeModel:
    def __init__(self):
        self.scenario = None
def neighbors(grid):
    px, py = int(grid.width / 2), int(grid.height / 2)
    neighbor_ids = grid.get_neighbors(px, py, 1)
    neighbor_ids = set([(neighbor_ids[i][0], neighbor_ids[i][1])
                        for i in range(len(neighbor_ids))])

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

    neighbor_ids = grid.get_neighbors(grid.width - 1, grid.height - 1, 1)
    grid.get_spot(0, 0)


def test_get_neighbors(grid):

    t0 = time.time()
    px = 1
    py = 2
    for i in range(100_000):
        grid.get_neighbors(px, py, 1)
    t1 = time.time()
    return t1-t0


def test_boost_grid():
    g1 = Grid(Spot, 100, 100, caching=False)
    g_fast = FastGrid(Spot, 100, 100, caching=False)
    # neighbors(g1)
    # neighbors(g_fast)
    print(g_fast.height)
    print(test_get_neighbors(g1))
    print(test_get_neighbors(g_fast))

def test_go_through(al):
    t0 = time.time()
    for i in range(1000):
        for agent in al:
            agent
    t1 = time.time()
    return t1-t0

def test_fast_agent_list():
    al = AgentList(NewAgent,1000, FakeModel())
    al_fast = FastAgentList(NewAgent,1000, FakeModel())
    print(test_go_through(al))
    print(test_go_through(al_fast))

# test_boost_grid()
test_fast_agent_list()