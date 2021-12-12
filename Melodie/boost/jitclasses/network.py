# -*- coding:utf-8 -*-
# @Time: 2021/11/28 10:21
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: network.py
import numba
import numpy as np
from numba import typeof, typed
from numba.experimental import jitclass
from numba.typed import Dict as NumbaDict
from numba.core import types
from .utils import dtype_detect

_jit_network_cls = None


def JITNetworkBackup(node_elem_cls):
    global _jit_network_cls
    node_dtypes = dtype_detect(node_elem_cls, (0,))

    agent_num = 100
    node_num = 2000
    edge_num = 8000
    nodes = np.zeros(node_num, dtype=node_dtypes)
    edges = np.array([(0, 0, 0) for i in range(edge_num)], dtype=[
        ('source', 'i8'),
        ('target', 'i8'),
        ('weight', 'f8'),
    ])

    agents_pos = np.array([-1 for i in range(agent_num)], dtype=np.int64)

    # 这个是一个缓存，用来存储临近的节点ID。
    # index_left: 左侧索引
    # index_right: 右侧索引
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

        def get_neighbor_ids(self, node_id: int):
            if self.edge_count == 0:
                return np.array([-1], dtype=np.int64)
            else:

                edges = self._edges["source"][:self.edge_count]
                cache = self._neighbors_cache[node_id]
                if cache[0] < 0:  # cache miss, search for edges.

                    bs = self.binsearch(edges, node_id)
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

        def get_neighbors(self, node):
            raise NotImplementedError

        @property
        def edges(self):
            return self._edges[:self.edge_count]

        def set_edge_property(self):
            pass

    _jit_network_cls = NetworkJIT
    return _jit_network_cls(nodes, edges, agents_pos, agents_on_node, neighbors_cache)


def JITNetwork(cache=True):
    global _jit_network_cls

    agent_num = 100
    node_num = 2000
    edge_num = 8000

    edges = np.array([(0, 0, 0) for i in range(edge_num)], dtype=[
        ('source', 'i8'),
        ('target', 'i8'),
        ('weight', 'f8'),
    ])

    agents_pos = np.array([-1 for i in range(agent_num)], dtype=np.int64)

    agents_on_node = -1 * np.ones((node_num, agent_num), dtype=np.int64)
    if _jit_network_cls is not None:
        return _jit_network_cls(edges, agents_pos, agents_on_node, cache=cache)

    @jitclass([
        # ('_nodes', numba.typeof(nodes)),
        ('_edges', numba.typeof(edges)),
        # ('_neighbors_cache', numba.typeof(neighbors_cache)),

        ('_agents_on_node', numba.typeof(agents_on_node)),
        ('node_count', types.int64),
        ('edge_count', types.int64),
        ('with_cache', types.boolean),

        # index代表节点属性数组_nodes的索引。
        # 同时也是_agent_ids的索引
        # {node_id_source: {node_id_target: index} }
        ('_adj', types.DictType(types.int64, types.DictType(types.int64, types.int64))),
        # 根据category和节点id，查询节点上所有agent的id {agent_category: [node_ids -> [agent_ids]] }
        ('_agent_ids', types.DictType(types.unicode_type, types.DictType(types.int64, types.ListType(types.int64)))),
        # 根据agent的category和id，反查agent的位置
        ('_agents_pos', types.DictType(types.unicode_type, types.DictType(types.int64, types.int64))),
        ('_neighbors_cache', types.DictType(types.int64, numba.typeof(np.array([1, 2, 3], dtype=np.int64)))),
    ])
    class NetworkJIT:
        def __init__(self, edges, agents_pos, agents_on_node, cache=True):
            # self._nodes = nodes
            self._edges = edges

            self._agents_on_node = agents_on_node

            self.node_count = 0
            self.edge_count = 0

            self._adj = typed.Dict.empty(types.int64, typed.Dict.empty(types.int64, types.int64))

            self._agent_ids = typed.Dict.empty(types.unicode_type,
                                               typed.Dict.empty(types.int64, typed.List.empty_list(types.int64)))
            self._agents_pos = typed.Dict.empty(types.unicode_type, typed.Dict.empty(types.int64, types.int64))

            self.with_cache = cache

            self._neighbors_cache = typed.Dict.empty(types.int64, np.array([1, 2, 3], dtype=np.int64))

        def add_category(self, category_name: str):
            """
            Add a category onto the network
            :param category_name: string
            :return:
            """
            self._agent_ids[category_name] = typed.Dict.empty(types.int64, typed.List.empty_list(types.int64))
            self._agents_pos[category_name] = typed.Dict.empty(types.int64, types.int64)

        def remove_edge(self, source_id, target_id):
            """
            Remove the edge from source_id to target_id
            :param source_id:
            :param target_id:
            :return:
            """
            assert self._adj[source_id].get(target_id) is not None
            self._adj[source_id].pop(target_id)

            assert self._adj[target_id].get(source_id) is not None

            self._adj[target_id].pop(source_id)

        def nodes(self):
            return self._adj.keys()

        def add_edge(self, source_id, target_id):
            if self._adj.get(source_id) is None:
                self._adj[source_id] = typed.Dict.empty(types.int64, types.int64)
            if self._adj.get(target_id) is None:
                self._adj[target_id] = typed.Dict.empty(types.int64, types.int64)
            self._adj[source_id][target_id] = 0
            self._adj[target_id][source_id] = 0
            self.edge_count += 1

        def add_agent(self, agent_id: int, category: str, node_id: int):
            """

            :param agent_id:
            :param category:
            :param node_id:
            :return:
            """

            assert self._agents_pos[category].get(agent_id) is None
            self._agents_pos[category][agent_id] = node_id
            if self._agent_ids[category].get(node_id) is None:
                self._agent_ids[category][node_id] = typed.List.empty_list(types.int64)
            self._agent_ids[category][node_id].append(agent_id)

        def remove_agent(self, agent_id: int, category: str):
            """

            :param agent_id:
            :param category:
            :return:
            """
            assert self._agents_pos[category].get(agent_id) is not None
            node_id = self._agents_pos[category].pop(agent_id)
            self._agent_ids[category][int(node_id)].remove(agent_id)

        def move_agent(self, agent_id: int, category: str, target_node_id: int):
            """

            :param agent_id:
            :param category:
            :param target_node_id:
            :return:
            """
            self.remove_agent(agent_id, category)
            self.add_agent(agent_id, category, target_node_id)

        def agent_pos(self, agent_id):

            node_id = self._agents_pos[agent_id]
            if node_id < 0:
                raise ValueError("agent not on the network!")
            else:
                return node_id

        def get_agents(self, category: str, node_id: int):
            """
            Get agents of a specific category at node_id
            :param category:
            :param node_id:
            :return:
            """
            agent_ids = self._agent_ids[category].get(node_id)
            if agent_ids is not None:
                return agent_ids
            else:
                return typed.List.empty_list(types.int64)

        def add_edges(self, ids_arr):
            """
            A numpy_array containing edges
            such as:
            np.array([(4, 0), (5, 0)], dtype=np.int64)
            will add two edges, 4 -> 0 and 5 -> 0
            :param ids_arr:
            :return:
            """

            length = len(ids_arr)
            for i in range(length):
                self.add_edge(ids_arr[i][0], ids_arr[i][1])

        def get_neighbors(self, node_id: int) -> np.ndarray:
            if self.with_cache:
                neighbor_ids = self._neighbors_cache.get(node_id)
                if neighbor_ids is None:

                    length = len(self._adj[node_id])

                    neighbor_ids = np.zeros(length, dtype=np.int64)
                    for i, target_id in enumerate(self._adj[node_id].keys()):
                        neighbor_ids[i] = target_id
                    self._neighbors_cache[node_id] = neighbor_ids
                return neighbor_ids
            else:
                length = len(self._adj[node_id])
                neighbor_ids = np.zeros(length, dtype=np.int64)
                for i, target_id in enumerate(self._adj[node_id].keys()):
                    neighbor_ids[i] = target_id
                self._neighbors_cache[node_id] = neighbor_ids
                return neighbor_ids

        @property
        def edges(self):
            return self._edges[:self.edge_count]

        def set_edge_property(self):
            pass

    _jit_network_cls = NetworkJIT
    return _jit_network_cls(edges, agents_pos, agents_on_node, cache=cache)
