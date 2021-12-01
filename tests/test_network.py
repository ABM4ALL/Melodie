# -*- coding:utf-8 -*-
# @Time: 2021/11/11 10:39
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: test_grid.py
import json
import random
import sys
import time

import numpy as np

from Melodie import AgentList, Agent
from Melodie import Network, Node
from Melodie.boost import JIT_AVAILABLE
import logging

from .config import model

logger = logging.getLogger(__name__)

N = 10000_000


class TestNode(Node):
    def setup(self):
        self.a = 123.0
        self.b = 456


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
    assert 3 not in network.get_neighbors(0)

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

    if isinstance(network, Network):
        t = run_without_jit(network)
        print("run without jit takes:", t)
    else:
        t = run_jit(network)
        print("run with jit takes:", t)


def test_network_JIT():
    if not JIT_AVAILABLE:
        return
    from Melodie.boost import JITNetwork
    network = JITNetwork(TestNode)
    network_routine(network)


def test_network_noJIT():
    from Melodie import Network
    network = Network()
    network_routine(network)

# @numba.njit
# def get_neighbors(graph, node, N):
#     s = 0
#     for i in range(N):
#         for n in graph.get_neighbors(node):
#             s += n
#     return s

# def main():
#     nodes = np.array([(i,)
#                       for i in range(100)
#                       ], dtype=[('id', 'i8')])
#     agents = np.array([(0,)], dtype=[('id', 'i8')])
#     node_arr = [node for node in nodes]
#     agent_arr = [agent for agent in agents]
#     n = build_jit_class(node_arr[0]['id'], agent_arr[0]['id'])
#     # index = n.binsearch(np.array([1, 4, 4, 4, 5, 5, 5, 8, 8, 8, 10]), 8, )
#     edges = [(0, i) for i in range(100)]
#     for e in edges:
#         n.add_edge(e[0], e[1])
#     for i in range(100):
#         n.add_agent(i, i)
#     # print(n.edges)
#     # print(neighbors := n.get_neighbors(0))
#     # for index in range(100):
#     #     print(agentpos := n.agent_pos(index))
#     #     print(neighbors := n.get_neighbors(agentpos))
#     #     if neighbors is not None:
#     #         print(len(neighbors))
#     #     else:
#     #         print("neighbors are None")
#     neighbors = n.get_neighbors(0)
#     print(n._agents_on_node)
#     N = 1000_000
#     return
#     t0 = time.time()
#
#     sum = get_neighbors(n, 0, N)
#     t1 = time.time()
#     print(t1 - t0, sum)
#
#     G = networkx.Graph()
#     G.add_edges_from(edges)
#
#     def run_nx():
#         sum = 0
#         for i in range(N):
#             for j in G.neighbors(0):
#                 sum += j
#         return sum
#
#     t0 = time.time()
#
#     print(run_nx())
#     t1 = time.time()
#     print(t1 - t0, sum)
#     print(n)
#
#
# if __name__ == '__main__':
#     main()
