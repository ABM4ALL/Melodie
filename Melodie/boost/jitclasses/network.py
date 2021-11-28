# -*- coding:utf-8 -*-
# @Time: 2021/11/28 10:21
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: network.py
import numba
import numpy as np
from numba import typeof
from numba.experimental import jitclass
from numba.typed import Dict as NumbaDict
from numba.core import types

_jit_network_cls = None


def JITNetwork(node_elem, agent_elem):
    global _jit_network_cls
    TYPE_NODE = typeof(node_elem)
    TYPE_AGENT = typeof(agent_elem)
    # _adj = NumbaDict.empty(key_type=types.int64, value_type=types.DictType(types.int64, types.int64))
    # _nodes = NumbaDict.empty(key_type=types.int64, value_type=numba.typeof(node_elem))
    # _agents = NumbaDict.empty(key_type=types.int64, value_type=types.DictType(types.int64, types.int64))
    # _agent_pos = NumbaDict.empty(key_type=types.int64, value_type=numba.typeof(agent_elem))
    agent_num = 100
    node_num = 2000
    edge_num = 8000
    nodes = np.array([(i, i) for i in range(node_num)], dtype=[('id', 'i8'), ('wealth', 'i8'), ])
    edges = np.array([(0, 0, 0) for i in range(edge_num)], dtype=[
        ('source', 'i8'),
        ('target', 'i8'),
        ('weight', 'f8'),
    ])
    agents_pos = np.array([-1 for i in range(agent_num)], dtype=np.int64)
    neighbors_cache = np.array([(-1, -1) for i in range(edge_num)], dtype=[
        ('index_left', 'i8'),
        ('index_right', 'i8'),
    ])
    agents_on_node = -1 * np.ones((node_num, agent_num), dtype=np.int64)
    if _jit_network_cls is not None:
        return _jit_network_cls(nodes, edges, agents_pos, agents_on_node, neighbors_cache)

    @jitclass([

        ('_nodes', numba.typeof(nodes)),
        ('_edges', numba.typeof(edges)),
        ('_neighbors_cache', numba.typeof(neighbors_cache)),
        ('_agents_pos', numba.typeof(agents_pos)),
        ('_agents_on_node', numba.typeof(agents_on_node)),
        ('node_count', types.int64),
        ('edge_count', types.int64),
    ])
    class NetworkJIT:
        def __init__(self, nodes, edges, agents_pos, agents_on_node, neighbors_cache):
            self._nodes = nodes
            self._edges = edges
            self._agents_pos = agents_pos
            self._agents_on_node = agents_on_node
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
            not_found = True
            while a < b:
                c = int((a + b) / 2)
                if arr[c] > value:
                    b = c
                elif arr[c] < value:
                    a = c
                else:
                    index = c
                    not_found = False
                    break
                if b == c or a == c:  # not in the list
                    break

            if not_found:
                return -1, -1
            index_left = index_right = index
            # print(index_left)
            while arr[index_left] == value and index_left > 0:
                index_left -= 1
            while arr[index_right] == value and index_right <= length:
                index_right += 1
            return index_left + 1, index_right

        def add_agent(self, agent_id, node_id):
            self._agents_pos[agent_id] = node_id
            self._add_agent_onto_node(agent_id, node_id)

        def _add_agent_onto_node(self, agent_id, node_id):
            pointer = -1  # pointer points to the first empty element.
            for i, original_agent_id in enumerate(self._agents_on_node[node_id]):
                if original_agent_id == agent_id:
                    return
                elif original_agent_id < 0:
                    pointer = i
                    break
            if pointer == -1:
                raise ValueError("Too many agents you are trying to add onto the node!")
            self._agents_on_node[node_id][pointer] = agent_id

        def agent_pos(self, agent_id):

            node_id = self._agents_pos[agent_id]
            if node_id < 0:
                raise ValueError("agent not on the network!")
            else:
                return node_id

        def add_edge(self, source_id, target_id):
            self._edges["source"][self.edge_count] = source_id
            self._edges["target"][self.edge_count] = target_id
            self.edge_count += 1

        def add_edges(self, source_ids, target_ids):
            assert len(source_ids) == len(target_ids)
            length = len(source_ids)
            for i in range(length):
                self._edges["source"][self.edge_count] = source_ids[i]
                self._edges["target"][self.edge_count] = target_ids[i]
                self.edge_count += 1

        def get_neighbor_ids(self, node_id: TYPE_NODE):
            if self.edge_count == 0:
                return np.array([-1], dtype=np.int64)
            else:

                edges = self._edges["source"][:self.edge_count]
                cache = self._neighbors_cache[node_id]
                if cache[0] < 0:  # cache miss, search for edges.

                    bs = self.binsearch(edges, node_id)
                    # print(bs,self.edge_count)
                    if bs[0] < 0:  # no neighbor!
                        return np.zeros(0, dtype=np.int64)

                    self._neighbors_cache[node_id][0] = bs[0]
                    self._neighbors_cache[node_id][1] = bs[1]
                else:  # cache hit.
                    bs = (cache[0], cache[1])
                res = np.zeros(bs[1] - bs[0], dtype=np.int64)
                for i in range(bs[0], bs[1]):
                    res[i] = self._edges["target"][i]
                return res

        def get_node_by_id(self, node_id: int):
            return self._nodes[node_id]

        def get_neighbors(self, node):
            raise NotImplementedError

        @property
        def edges(self):
            return self._edges[:self.edge_count]

        def set_edge_property(self):
            pass

    _jit_network_cls = NetworkJIT
    return _jit_network_cls(nodes, edges, agents_pos, agents_on_node, neighbors_cache)
