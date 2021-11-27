import logging
import sys
import json
from typing import Dict, Tuple, List

from Melodie import DataCollector

sys.path.append("../..")
# Melody package is not available on pip yet, so this example has to import Melody package placed at project root.
# Appending project root to "sys.path" makes Melody package accessible to the interpreter.
# This code will be removed as soon as we release the first distribution onto pip.
from model.agent import FuncAgent
from model.environment import FuncEnvironment
from model.scenario import FuncScenario
from model.model import FuncModel
from model.simulator import FuncSimulator
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

if __name__ == "__main__":
    simulator = FuncSimulator()

    """
    Run the model with simulator
    """
    simulator.run(
        agent_class=FuncAgent,
        environment_class=FuncEnvironment,
        config=config,
        model_class=FuncModel,
        scenario_class=FuncScenario,
        data_collector_class=DataCollector
        # analyzer_class=Analyzer
    )
