import logging
import os
import sys
import time
import json
from typing import Dict, Tuple, List

import numpy as np

sys.path.append("../..")
# Melody package is not available on pip yet, so this example has to import Melody package placed at project root.
# Appending project root to "sys.path" makes Melody package accessible to the interpreter.
# This code will be removed as soon as we release the first distribution onto pip.
from model.agent import FuncAgent
from model.environment import FuncEnvironment
from model.scenario import FuncScenario
from model.model import FuncModel
from model.simulator import FuncSimulator
from analyzer.analyzer import Analyzer
from Melodie.network import build_jit_class
from config import config

logger = logging.getLogger(__name__)

node_names_map: Dict[str, int] = {}
edges_with_num: List[Tuple[int, int]] = []
with open("./data/json_source/lua_call_graph.json") as f:
    network_json = json.load(f)
    edges = network_json['series']['links']
    node_names = set()
    for link in edges:
        node_names.add(link['source'])
        node_names.add(link['target'])
    for i, node_name in enumerate(node_names):
        node_names_map[node_name] = i
    for edge in edges:
        edges_with_num.append((node_names_map[edge['source']], node_names_map[edge['target']]))
        # if link[0] not in edge_names:
        #     edge_names[link[0]]
edges_array = np.array(edges_with_num, dtype=np.int64)


class BoostModel:
    def __init__(self, scenario):
        node_num = len(list(node_names))

        self.environment = np.array([(100, 0.6, 0, 0)],
                                    dtype=[('trade_num', 'i4'),
                                           ('win_prob', 'f4'),
                                           ('total_wealth', 'i4'),
                                           ('gini', 'f4')])[0]

        self.agent_list = np.array([(i, 0.99, 0) for i in range(node_num)],
                                   dtype=[('id', 'i4'),
                                          ('reliability', 'f4'),
                                          ('status', 'i4'),
                                          ])

        self.scenario = scenario
        nodes = np.array([(i,)
                          for i in range(node_num)
                          ], dtype=[('id', 'i8')])

        # node_arr = [node for node in nodes]
        t0 = time.time()
        n = build_jit_class(nodes[0]['id'], self.agent_list[0]['id'])

        # n.add_edges(edges_array[:, 0], edges_array[:, 1])
        for e in edges_with_num:
            n.add_edge(e[0], e[1])
        t1 = time.time()
        self.network = n
        # print(n.get_neighbors(0))
        # sys.exit()

        logger.info(f"Initializing the graph. Time elapsed:{t1 - t0}")


if __name__ == "__main__":
    simulator = FuncSimulator()

    """
    Run the model with simulator
    """
    simulator.run_boost(
        FuncAgent,
        FuncEnvironment,
        config,
        model_class=FuncModel,
        scenario_class=FuncScenario,
        analyzer_class=Analyzer,
        boost_model_class=BoostModel
    )
