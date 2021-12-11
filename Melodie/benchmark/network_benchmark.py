# -*- coding:utf-8 -*-
# @Time: 2021/12/8 10:45
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: network_benchmark.py
import time

import networkx as nx
from Melodie.boost import JITNetwork
from Melodie import Network
import matplotlib.pyplot as plt
import numba
import logging

logging.basicConfig(level=logging.INFO)


class A:
    def __init__(self):
        a = 1


def walk_neighbors_nojit(network: Network, nodes):
    for i in range(1000):
        for n in range(nodes):
            for neighbor in network.get_neighbors(n):
                s = neighbor

    return s


@numba.njit
def walk_neighbors_jit(network: Network, nodes):
    for i in range(1000):
        for n in range(nodes):
            for neighbor in network.get_neighbors(n):
                s = neighbor
    return s


def main():
    print('nodes', 'with_jit_after_compiling', "with_jit_before_compiling", "without_jit")
    x = []
    t_with_jit = []
    t_with_jit_without_cache = []
    t_without_jit = []
    # t_without_jit = []
    for i, nodes in enumerate([10, 10, 50, 100, 300, 500, 1000, 2000, 5000]):

        g = nx.watts_strogatz_graph(nodes, 3, 0.1)
        jit_nw = JITNetwork(cache=True)
        jit_nw_without_cache = JITNetwork(cache=False)
        nw = Network()
        for e in g.edges:
            jit_nw.add_edge(e[0], e[1])
            nw.add_edge(e[0], e[1])
            jit_nw_without_cache.add_edge(e[0], e[1])

        t0 = time.time()
        walk_neighbors_nojit(nw, nodes)
        t1 = time.time()
        walk_neighbors_jit(jit_nw_without_cache, nodes)
        t2 = time.time()
        walk_neighbors_jit(jit_nw, nodes)
        t3 = time.time()
        print(nodes, t3 - t2, t2 - t1, t1 - t0)
        if i > 0:  # The first time was for jit to warm up
            x.append(nodes)

            t_with_jit.append((t3 - t2) / 1000)
            t_with_jit_without_cache.append((t2 - t1) / 1000)
            t_without_jit.append((t1 - t0) / 1000)
    plt.title("Time consumption")
    plt.plot(x, t_with_jit, label="JIT and Cache")
    plt.plot(x, t_with_jit_without_cache, label="JIT no Cache")
    plt.plot(x, t_without_jit, label="No JIT")
    plt.xlabel('Nodes')
    plt.ylabel("Time/s")

    plt.legend()
    plt.grid()
    plt.show()


main()
