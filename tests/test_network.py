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
    pass


def test_network():
    n = Network(TestNode)
    n.add_edge(0, 1)
    n.add_edge(0, 2)
    n.add_edge(0, 3)
    n.add_edge(0, 4)


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
