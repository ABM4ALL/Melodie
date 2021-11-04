# network是定义在agent上的，不像grid那么独立。没有人，地球上依然有土地。但是，没有人，也有不存在“人和人之间的关系”了。
# 用一张矩阵记录agent之间的【关系】，关系又可以有多个属性，方向、每个方向的强弱等。
# agent和env都可以访问network并修改agent之间的【关系】
# network是run_model的可选项，如果选了，就初始化到model里
import numba
import numpy as np
from numba import typeof
from numba.experimental import jitclass
from numba.typed import Dict as NumbaDict
from numba.typed import List as NumbaList
from numba.core import types
from Melodie.agent import Agent
from Melodie.agent_manager import AgentList
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
    _adj = NumbaDict.empty(key_type=types.int64, value_type=types.DictType(types.int64, types.int64))
    _nodes = NumbaDict.empty(key_type=types.int64, value_type=numba.typeof(node_elem))
    _agents = NumbaDict.empty(key_type=types.int64, value_type=types.DictType(types.int64, types.int64))
    _agent_pos = NumbaDict.empty(key_type=types.int64, value_type=numba.typeof(agent_elem))

    @jitclass([
        ('_adj', types.DictType(types.int64, types.DictType(types.int64, types.int64))),
        ('_nodes', types.DictType(types.int64, TYPE_NODE)),
        ('_agents', types.DictType(types.int64, types.DictType(types.int64, types.int64))),
        ('_agent_pos', types.DictType(types.int64, types.int64)),  # Which node was the agent on
    ])
    class NetworkJIT:
        def __init__(self, adj, nodes, agents, agent_pos):
            self._adj = adj
            self._nodes = nodes

            self._agents = agents  # {node_id: {agent_id: agent_id}}
            self._agent_pos = agent_pos

        def place_agent(self, node, agent):
            node_id = node['id']
            agent_id = agent['id']
            if self._agents.get(node['id']) is None:
                if self._agent_pos.get(agent_id) is not None:
                    raise ValueError(f"Agent already on the network!")
                self._agents[node['id']] = NumbaDict.empty(key_type=types.int64, value_type=types.int64)
            self._agents[node['id']][agent_id] = agent_id
            if self._agent_pos.get(agent_id) is None:
                self._agent_pos[agent_id] = node_id

        def get_agents(self, node):
            pos = self._agents[node['id']]
            # for i in pos.keys()
            return pos

        def add_edge(self, source: Node, target: Node):
            source_id = source['id']
            target_id = target['id']
            _adj = self._adj
            _nodes = self._nodes
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

        def set_edge_property(self):
            pass

        def get_neighbors(self):
            pass

    return NetworkJIT(_adj, _nodes, _agents, _agent_pos)


if __name__ == '__main__':
    nodes = np.array([(0,),
                      (1,),
                      (2,),
                      (3,),
                      (4,),
                      (5,),
                      (6,),
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
    # ___network___add_edge(_nodes, _adj, )
    for i in range(len(node_arr) - 1):
        # ___network___add_edge(_nodes, _adj, node_list[i], node_list[i + 1])
        n.add_edge(node_arr[i], node_arr[i + 1])
        n.place_agent(node_arr[i], agent_arr[i])
    print(n._adj)
    print(n._agents)
    print(n.get_agents(node_arr[0]))
