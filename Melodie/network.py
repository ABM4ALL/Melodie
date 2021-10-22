# network是定义在agent上的，不像grid那么独立。没有人，地球上依然有土地。但是，没有人，也有不存在“人和人之间的关系”了。
# 用一张矩阵记录agent之间的【关系】，关系又可以有多个属性，方向、每个方向的强弱等。
# agent和env都可以访问network并修改agent之间的【关系】
# network是run_model的可选项，如果选了，就初始化到model里
import time

import networkx
import numba
import numpy as np
from numba import typeof
from numba.experimental import jitclass
from numba.typed import Dict as NumbaDict
from numba.core import types
from Melodie.agent import Agent
import logging

logging.basicConfig(level=logging.DEBUG)


class Node(Agent):
    pass


@numba.njit
def ___network___add_edge(_nodes, _adj, source, target):
    source_id = source['id']
    target_id = target['id']
    print("got :", _nodes.get(source_id))
    if _nodes.get(source_id) is None:
        _nodes[source_id] = source

    if _nodes.get(target_id) is None:
        _nodes[target_id] = target

    if _adj.get(source_id) is None:
        _adj[source_id] = NumbaDict.empty(
            key_type=types.int64,
            value_type=types.int64
        )
    _adj[source_id][target_id] = 1

    if _adj.get(target_id) is None:
        _adj[target_id] = NumbaDict.empty(
            key_type=types.int64,
            value_type=types.int64
        )
    _adj[target_id][source_id] = 1


def build_jit_class(node_elem, agent_elem):
    TYPE_NODE = typeof(node_elem)
    TYPE_AGENT = typeof(agent_elem)
    # _adj = NumbaDict.empty(key_type=types.int64, value_type=types.DictType(types.int64, types.int64))
    # _nodes = NumbaDict.empty(key_type=types.int64, value_type=numba.typeof(node_elem))
    # _agents = NumbaDict.empty(key_type=types.int64, value_type=types.DictType(types.int64, types.int64))
    # _agent_pos = NumbaDict.empty(key_type=types.int64, value_type=numba.typeof(agent_elem))
    nodes = np.array([(i, i) for i in range(100)], dtype=[('id', 'i8'), ('wealth', 'i8'), ])
    edges = np.array([(0, 0, 0) for i in range(1000)], dtype=[
        ('source', 'i8'),
        ('target', 'i8'),
        ('weight', 'f8'),
    ])
    neighbors_cache = np.array([(-1, -1) for i in range(1000)], dtype=[
        # ('node', 'i8'),
        ('index_left', 'i8'),
        ('index_right', 'i8'),
    ])

    @jitclass([
        # ('_adj', types.DictType(types.int64, types.DictType(types.int64, types.int64))),
        ('_nodes', numba.typeof(nodes)),
        ('_edges', numba.typeof(edges)),
        ('_neighbors_cache', numba.typeof(neighbors_cache)),
        ('node_count', types.int64),
        ('edge_count', types.int64),
    ])
    class NetworkJIT:
        def __init__(self, nodes, edges, neighbors_cache):
            self._nodes = nodes
            self._edges = edges
            self._neighbors_cache = neighbors_cache
            self.node_count = 0
            self.edge_count = 0

        def binsearch(self, arr, value):
            """
            返回一个范围的索引。
            :param arr:
            :param value:
            :return:
            """
            a = 0
            length = len(arr)
            b = len(arr)
            c = 0
            index = -1
            while a < b:
                c = int((a + b) / 2)
                if arr[c] > value:
                    b = c
                elif arr[c] < value:
                    a = c
                else:
                    index = c
                    break
            index_left = index_right = index
            print(index_left)
            while arr[index_left] == value and index_left > 0:
                index_left -= 1
            while arr[index_right] == value and index_right <= length:
                index_right += 1
            return index_left + 1, index_right

        def add_edge(self, source, target):
            source_id = source['id']
            target_id = target['id']
            self._edges["source"][self.edge_count] = source_id
            self._edges["target"][self.edge_count] = target_id
            self.edge_count += 1

        def get_neighbors(self, node: TYPE_NODE):
            if self.edge_count == 0:
                return np.array([-1], dtype=np.int64)
            else:
                edges = self._edges["source"][:self.edge_count]
                cache = self._neighbors_cache[node['id']]
                if cache[0] < 0:  # cache miss, search for edges.
                    bs = self.binsearch(edges, node['id'])
                    self._neighbors_cache[node['id']][0] = bs[0]
                    self._neighbors_cache[node['id']][1] = bs[1]
                else: # cache hit.
                    bs = (cache[0], cache[1])
                res = np.zeros(bs[1] - bs[0], dtype=np.int64)
                for i in range(bs[0], bs[1]):
                    res[i] = self._edges["target"][i]
                return res

        @property
        def edges(self):
            return self._edges[:self.edge_count]

        def set_edge_property(self):
            pass

    return NetworkJIT(nodes, edges, neighbors_cache)  # _adj, _nodes, _agents, _agent_pos)


@numba.njit
def get_neighbors(graph, node, N):
    s = 0
    for i in range(N):
        for n in graph.get_neighbors(node):
            s += n
    return s


# def f():
def main():
    nodes = np.array([(i,)
                      for i in range(100)
                      ], dtype=[('id', 'i8')])
    agents = np.array([(0,),
                       (1,),
                       (2,),
                       (3,),
                       (4,),
                       (5,),
                       (6,),
                       ], dtype=[('id', 'i8')])
    node_arr = [node for node in nodes]
    agent_arr = [agent for agent in agents]
    n = build_jit_class(node_arr[0], agent_arr[0])
    # index = n.binsearch(np.array([1, 4, 4, 4, 5, 5, 5, 8, 8, 8, 10]), 8, )
    edges = [(0, i) for i in range(100)]
    for e in edges:
        n.add_edge(node_arr[e[0]], node_arr[e[1]])
    print(n.edges)
    print(neighbors := n.get_neighbors(node_arr[0]))
    print(len(neighbors))
    # return
    N = 1000_000

    # get_neighbors(n, node_arr[0], N)
    t0 = time.time()

    sum = get_neighbors(n, node_arr[0], N)
    t1 = time.time()
    print(t1 - t0, sum)

    G = networkx.Graph()
    G.add_edges_from(edges)

    def run_nx():
        sum = 0
        for i in range(N):
            for j in G.neighbors(0):
                sum += j
        return sum

    t0 = time.time()

    print(run_nx())
    t1 = time.time()
    print(t1 - t0, sum)
    print(n)


if __name__ == '__main__':
    main()
# n.get_neighbors(nodes[0], )
# print(neighbors)
# ___network___add_edge(_nodes, _adj, )
# for i in range(len(node_arr) - 1):
#     # ___network___add_edge(_nodes, _adj, node_list[i], node_list[i + 1])
#     n.add_edge(node_arr[i], node_arr[i + 1])
#     n.place_agent(node_arr[i], agent_arr[i])
# print(n._adj)
# print(n._agents)
# print(n.get_agents(node_arr[0]))
