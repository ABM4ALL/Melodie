import logging
import os
import sys
import time
import json
from typing import Dict, Tuple, List

import numpy as np

from examples.GameOfLifeNew.model.spot import GameOfLifeSpot

sys.path.append("../..")
# Melody package is not available on pip yet, so this example has to import Melody package placed at project root.
# Appending project root to "sys.path" makes Melody package accessible to the interpreter.
# This code will be removed as soon as we release the first distribution onto pip.
from model.environment import GameOfLifeEnvironment, Strategy1, Strategy
from model.scenario import GameOfLifeScenario
from model.model import GameOfLifeModel
from model.simulator import FuncSimulator
from model.visualizer import GameOfLifeVisualizer
from analyzer.analyzer import Analyzer
from config import config

logger = logging.getLogger(__name__)

from Melodie.boost.compiler.typeinferlib import register_type
from Melodie.boost.compiler.class_compiler import add_custom_jit_class

register_type(GameOfLifeSpot)
register_type(Strategy1)
register_type(Strategy)
add_custom_jit_class(Strategy1)
logging.basicConfig(level=logging.INFO)
if __name__ == "__main__":
    simulator = FuncSimulator()

    """
    Run the model with simulator
    """
    simulator.run_boost(
        [GameOfLifeSpot],
        GameOfLifeEnvironment,
        config,
        model_class=GameOfLifeModel,
        scenario_class=GameOfLifeScenario,
        analyzer_class=Analyzer,
        boost_model_class=GameOfLifeModel,
        model_components=None,
        visualizer_class=GameOfLifeVisualizer
    )
