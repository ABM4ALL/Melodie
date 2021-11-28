# network是定义在agent上的，不像grid那么独立。没有人，地球上依然有土地。但是，没有人，也有不存在“人和人之间的关系”了。
# 用一张矩阵记录agent之间的【关系】，关系又可以有多个属性，方向、每个方向的强弱等。
# agent和env都可以访问network并修改agent之间的【关系】
# network是run_model的可选项，如果选了，就初始化到model里
import json
import threading
import time
from queue import Queue
from typing import Dict, Set, Union, List, Tuple, Callable, Any, ClassVar

import numpy as np

from Melodie.agent import Agent
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Node(Agent):
    def __init__(self, node_id: int):
        super(Node, self).__init__(node_id)


class Network:
    def __init__(self, node_cls: ClassVar['Node']):
        self.simple = True
        self._node_cls = node_cls
        self._nodes: Dict[int, Node] = {}
        self._adj: Dict[int, Union[Set[int], List[int]]] = {}

    def get_node_by_id(self, node_id: int) -> Node:
        return self._nodes[node_id]

    def add_node(self, node: Node):
        assert node.id not in self._nodes
        self._nodes[node.id] = node

    def add_edge(self, source: int, target: int):
        assert isinstance(source, int)
        assert isinstance(target, int)
        self._nodes[source] = source
        self._nodes[target] = target

        if source not in self._adj.keys():
            self._adj[source] = set() if self.simple else list()
        if target not in self._adj.keys():
            self._adj[target] = set() if self.simple else list()
        self._adj[source].add(target)
        self._adj[target].add(source)

    def get_neighbors(self, node: int) -> List[int]:

        neighbor_ids = self._adj.get(node)
        if neighbor_ids is None:
            return []
        else:
            return neighbor_ids

    # def get_neighbors(self, node: Node) -> List[Node]:
    #     assert isinstance(node, Node)
    #     neighbor_ids = self.get_neighbor_ids(node)
    #     return [self._nodes[neighbor_id] for neighbor_id in neighbor_ids]


class NetworkDirected(Network):
    def __init__(self):
        super(NetworkDirected, self).__init__()

    def add_edge(self, source, target):
        pass

    def get_neighbors(self, node):
        pass



