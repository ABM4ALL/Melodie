import sys

from Melodie import DataCollector

sys.path.append("../..")
# Melody package is not available on pip yet, so this example has to import Melody package placed at project root.
# Appending project root to "sys.path" makes Melody package accessible to the interpreter.
# This code will be removed as soon as we release the first distribution onto pip.

from model.environment import GameOfLifeEnvironment
from model.scenario import GameOfLifeScenario
from model.model import GameOfLifeModel
from model.simulator import FuncSimulator
from model.visualizer import GameOfLifeVisualizer
from config import config

if __name__ == "__main__":
    simulator = FuncSimulator()

    """
    Run the model with dataframe_loader.rst
    """
    simulator.run_visual(
        agent_class=None,
        environment_class=GameOfLifeEnvironment,
        config=config,
        model_class=GameOfLifeModel,
        scenario_class=GameOfLifeScenario,
        data_collector_class=DataCollector,
        visualizer_class=GameOfLifeVisualizer
    )
