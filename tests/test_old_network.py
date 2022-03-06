# -*- coding:utf-8 -*-
# @Time: 2021/11/11 10:39
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: test_grid.py

import time

import numpy as np

from Melodie import OldNetwork
from Melodie.boost import JIT_AVAILABLE
import logging

logger = logging.getLogger(__name__)

N = 10000_000


def run_jit(network):
    import numba
    @numba.njit
    def get_neighbor_jit(network):
        s0 = 0
        for i in range(1000_000):
            ids = network.get_neighbors(0)
            for i in ids:
                s0 += i

    get_neighbor_jit(network)
    t0 = time.time()
    get_neighbor_jit(network)
    t1 = time.time()
    return t1 - t0


def run_without_jit(network):
    def f(network):
        s = 0
        for i in range(1000_000):
            neighbors = network.get_neighbors(0)
            for neighbor in neighbors:
                s += neighbor

    t0 = time.time()
    f(network)
    t1 = time.time()
    return t1 - t0


def network_routine(network):
    network.add_category('wolves')
    network.add_category('sheep')
    network.add_edge(0, 1)
    network.add_edge(0, 2)
    network.add_edge(0, 3)
    network.add_edges(np.array([(4, 0), (5, 0)], dtype=np.int64))
    network.add_edges(np.array([(1, 2), (1, 3)], dtype=np.int64))

    assert len(network.get_neighbors(0)) == 5
    assert len(network.get_neighbors(1)) == 3
    assert 0 in network.get_neighbors(1)
    assert 2 in network.get_neighbors(1)
    assert 3 in network.get_neighbors(1)

    network.remove_edge(0, 3)
    assert 3 not in list(network.get_neighbors(0))

    network.add_agent(0, 'wolves', 0)
    network.add_agent(1, 'wolves', 0)
    network.add_agent(2, 'wolves', 0)
    network.add_agent(1, 'sheep', 1)

    assert len(network.get_agents('wolves', 0)) == 3
    assert len(network.get_agents('sheep', 1)) == 1
    assert len(network.get_agents('sheep', 0)) == 0
    # network.remove_agent(1,'sheep')
    network.move_agent(1, 'sheep', 0)
    assert len(network.get_agents('sheep', 1)) == 0
    assert len(network.get_agents('sheep', 0)) == 1

    if isinstance(network, OldNetwork):
        t = run_without_jit(network)
        print("run without jit takes:", t)
    else:
        t = run_jit(network)
        print("run with jit takes:", t)


# def test_network_JIT():
#     if not JIT_AVAILABLE:
#         return
#     from Melodie.boost import JITNetwork
#     network = JITNetwork()
#     network_routine(network)


def test_network_noJIT():
    from Melodie import OldNetwork
    network = OldNetwork()
    network_routine(network)
