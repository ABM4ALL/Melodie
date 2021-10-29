# -*- coding: utf-8 -*-
__author__ = 'Songmin'

import json
from typing import Dict, List, Tuple

from Melodie import Model
from Melodie.network import Network, Node


class FuncNode(Node):
    def setup(self):
        pass


class FuncModel(Model):
    def setup(self):
        self.network = Network()
        node_names_map: Dict[str, int] = {}
        edges_with_num: List[Tuple[int, int]] = []
        with open("./data/json_source/lua_call_graph.json") as f:
            network_json = json.load(f)
            edges = network_json['series']['links']
            node_names = set()
            for link in edges:
                node_names.add(link['from'])
                node_names.add(link['to'])
            for i, node_name in enumerate(node_names):
                node_names_map[node_name] = i
            for edge in edges:
                edges_with_num.append((node_names_map[edge['from']], node_names_map[edge['to']]))
        for e in edges_with_num:
            self.network.add_edge(Node(e[0]), Node(e[1]))

    def run(self):
        agent_manager = self.agent_manager
        for t in range(0, self.scenario.periods):
            self.environment.step(agent_manager, self.network)
        print(self.agent_manager.agents)