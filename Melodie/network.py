
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


class Edge:
    # 单项/双向
    # 道路限速
    pass

class Network:
    def __init__(self):
        self.simple = True
        self._nodes: Set[int] = set()
        self._adj: Dict[int, Union[Set[int], List[int]]] = {}
        self._agent_ids: Dict[str, Dict[int, Set[int]]] = {}  # {'wolves': {0 : set(1, 2, 3)}}， 代表0号节点上有1,2,3三只狼
        self._agent_pos: Dict[str, Dict[int, int]] = {}  # {'wolves': {0: 1}}代表0号狼位于1节点

    def add_category(self, category_name: str):
        """
        Add category
        :param category_name:
        :return:
        """
        self._agent_ids[category_name] = {}
        self._agent_pos[category_name] = {}

    def add_node(self, node: int):
        # 可以删掉，只用add_agent，因为agent就是node
        assert node not in self._nodes

    def add_edge(self, source_id: int, target_id: int):
        """
        Add an edge onto the network.
        :param source_id: 
        :param target_id: 
        :return: 
        """
        if source_id not in self._nodes:
            self.add_node(source_id)
        if target_id not in self._nodes:
            self.add_node(target_id)

        if source_id not in self._adj.keys():
            self._adj[source_id] = set()
        if target_id not in self._adj.keys():
            self._adj[target_id] = set()
        self._adj[source_id].add(target_id)
        self._adj[target_id].add(source_id)

    def remove_edge(self, source_id: int, target_id: int):
        """
        Remove an edge from the network
        :param source_id:
        :param target_id:
        :return:
        """
        self._adj[source_id].remove(target_id)
        self._adj[target_id].remove(source_id)

    def get_neighbors(self, node: int) -> List[int]:

        neighbor_ids = self._adj.get(node)
        if neighbor_ids is None:
            return []
        else:
            return neighbor_ids

    def add_edges(self, edges: List[Tuple[int, int]]):
        for edge in edges:
            self.add_edge(edge[0], edge[1])

    def add_agent(self, agent_id: int, category: str, node_id: int):
        """

        :param agent_id:
        :param category:
        :param node_id:
        :return:
        """
        assert agent_id not in self._agent_ids
        if node_id not in self._agent_ids[category]:
            self._agent_ids[category][node_id] = set()
        self._agent_ids[category][node_id].add(agent_id)
        self._agent_pos[category][agent_id] = node_id

    def remove_agent(self, agent_id: int, category: str):
        """

        :param agent_id:
        :param category:
        :return:
        """
        assert category in self._agent_ids
        node_id: int = self._agent_pos[category].pop(agent_id)
        self._agent_ids[category][node_id].remove(agent_id)

    def move_agent(self, agent_id: int, category: str, target_node_id: int):
        """

        :param agent_id:
        :param category:
        :param target_node_id:
        :return:
        """
        self.remove_agent(agent_id, category)
        self.add_agent(agent_id, category, target_node_id)

    def get_agents(self, category: str, node_id: int):
        """

        :param category:
        :param node_id:
        :return:
        """
        if node_id not in self._agent_ids[category].keys():
            return set()
        else:
            return self._agent_ids[category][node_id]

    def agent_pos(self, agent_id: int, category: str):
        return self._agent_pos[category][agent_id]

    def create_edge(self,
                    category_1: str, agent_1_id: int,
                    category_2: str, agent_2_id: int,
                    **edge_properties):
        edge = Edge(category_1, agent_1_id,
                    category_2, agent_2_id,
                    edge_properties)
        self.add_edge(edge)



class NetworkDirected(Network):
    def __init__(self):
        super(NetworkDirected, self).__init__()

    def add_edge(self, source, target):
        pass

    def get_neighbors(self, node):
        pass



class SomeModel:

    def setup_agent_list(self):
        self.persons = []
        self.medias = []

    def setup_network(self):
        self.network = Network()
        self.network.add_category("persons")
        self.network.add_category("medias")
        self.network.add_agent("persons", self.persons[0])
        self.network.add_agent("persons", self.persons[1])
        self.network.create_edge("persons", self.persons[0], "persons", self.persons[1], )

        pass
    pass