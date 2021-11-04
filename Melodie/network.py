# network是定义在agent上的，不像grid那么独立。没有人，地球上依然有土地。但是，没有人，也有不存在“人和人之间的关系”了。
# 用一张矩阵记录agent之间的【关系】，关系又可以有多个属性，方向、每个方向的强弱等。
# agent和env都可以访问network并修改agent之间的【关系】
# network是run_model的可选项，如果选了，就初始化到model里
import json
import threading
import time
from queue import Queue
from typing import Dict, Set, Union, List, Tuple, Callable, Any

import networkx
import numba
import numpy as np
from numba import typeof
from numba.experimental import jitclass
from numba.typed import Dict as NumbaDict
from numba.core import types
from Melodie.agent import Agent
import logging

from Melodie.management.manager_server import run_visualize, visualize_condition_queue_main, \
    visualize_condition_queue_server

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Node(Agent):
    def __init__(self, node_id: int):
        super(Node, self).__init__(node_id)


class NetworkVisualizer():
    def __init__(self):

        def f123123():
            t0 = time.time()
            visualize_condition_queue_main.put(True)
            ret = visualize_condition_queue_server.get()
            t1 = time.time()

            return json.dumps(ret, indent=4)  # f"{t1 - t0}"

        self.server_thread, self.visualize_server = run_visualize(f123123)

        logger.info("Network visualizer server is starting...")
        self.vertex_positions: Dict[str, Tuple[int, int]] = {}
        self.vertex_roles: Dict[str, int] = {}

        self.edge_roles: Dict[Tuple[int, int], int] = {}

    def parse_edges(self, edges: List[Any], parser: Callable):

        for edge in edges:
            edge, pos = parser(edge)
            self.edge_roles[edge] = pos

    def parse_layout(self, node_info: List[Any],
                     parser: Callable[[Any], Tuple[Union[str, int], Tuple[float, float]]] = None):
        """

        :param node_info: A list contains a series of node information.
        :return:
        """
        if parser is None:
            parser = lambda node: (node['name'], (node['x'], node['y']))
        for node in node_info:
            node_name, pos = parser(node)
            self.vertex_positions[node_name] = pos

    def parse_role(self, node_info: List[Any],
                   parser: Callable[[Any], int] = None):
        """

        :param node_info: A list contains a series of node information.
        :return:
        """
        assert parser is not None
        for node in node_info:
            node_name, role = parser(node)
            print(node_name, role, node)
            assert isinstance(role, int), "The role of node should be an int."
            self.vertex_roles[node_name] = role

    def format(self):
        lst = []
        for name, pos in self.vertex_positions.items():
            lst.append(
                {
                    "name": name,
                    "x": pos[0],
                    "y": pos[1],
                    "category": self.vertex_roles[name]
                }
            )
        lst_edges = []
        for edge, role in self.edge_roles.items():
            lst_edges.append({
                "source": edge[0],
                "target": edge[1]
            })
        data = {
            "series": {
                "data": lst,
                "links": lst_edges
            }
        }
        return data

    def wait(self):
        # print("主线程等待！", visualize_condition_queue_main)
        visualize_condition_queue_main.get()
        # print("主线程开始执行！")
        formatted = self.format()
        visualize_condition_queue_server.put(formatted)
        # print("主线程执行完成！")


class Network:
    def __init__(self):
        self.simple = True
        self._nodes: Dict[int, Node] = {}
        self._adj: Dict[int, Union[Set[int], List[int]]] = {}

    def get_node_by_id(self, node_id: int) -> Node:
        return self._nodes[node_id]

    def add_node(self, node: Node):
        assert node.id not in self._nodes
        self._nodes[node.id] = node

    def add_edge(self, source: Node, target: Node):
        assert isinstance(source, Node) and isinstance(target, Node)
        self._nodes[source.id] = source
        self._nodes[target.id] = target

        if source.id not in self._adj.keys():
            self._adj[source.id] = set() if self.simple else list()
        if target.id not in self._adj.keys():
            self._adj[target.id] = set() if self.simple else list()
        self._adj[source.id].add(target.id)
        self._adj[target.id].add(source.id)

    def get_neighbor_ids(self, node_id: Node) -> List[int]:
        assert node_id in self._nodes
        neighbor_ids = self._adj.get(node_id)
        if neighbor_ids is None:
            return []
        else:
            return neighbor_ids

    def get_neighbors(self, node: Node) -> List[Node]:
        assert isinstance(node, Node)
        neighbor_ids = self.get_neighbor_ids(node)
        return [self._nodes[neighbor_id] for neighbor_id in neighbor_ids]


class NetworkDirected(Network):
    def __init__(self):
        super(NetworkDirected, self).__init__()

    def add_edge(self, source, target):
        pass

    def get_neighbors(self, node):
        pass


_jit_network_cls = None


def build_jit_class(node_elem, agent_elem):
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
    agents = np.array([(0,)], dtype=[('id', 'i8')])
    node_arr = [node for node in nodes]
    agent_arr = [agent for agent in agents]
    n = build_jit_class(node_arr[0]['id'], agent_arr[0]['id'])
    # index = n.binsearch(np.array([1, 4, 4, 4, 5, 5, 5, 8, 8, 8, 10]), 8, )
    edges = [(0, i) for i in range(100)]
    for e in edges:
        n.add_edge(e[0], e[1])
    for i in range(100):
        n.add_agent(i, i)
    # print(n.edges)
    # print(neighbors := n.get_neighbors(0))
    # for index in range(100):
    #     print(agentpos := n.agent_pos(index))
    #     print(neighbors := n.get_neighbors(agentpos))
    #     if neighbors is not None:
    #         print(len(neighbors))
    #     else:
    #         print("neighbors are None")
    print(neighbors := n.get_neighbors(0))
    print(n._agents_on_node)
    N = 1000_000
    return
    t0 = time.time()

    sum = get_neighbors(n, 0, N)
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
