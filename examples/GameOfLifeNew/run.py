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
from Melodie.visualization import GridVisualizer
from config import config

if __name__ == "__main__":
    simulator = FuncSimulator()

    """
    Run the model with register.rst
    """
    simulator.run(config, GameOfLifeModel, GameOfLifeScenario)

    # register.rst.run_visual(
    #     # agent_class=None,
    #     # environment_class=GameOfLifeEnvironment,
    #     config=config,
    #     model_class=GameOfLifeModel,
    #     scenario_class=GameOfLifeScenario,
    #     # data_collector_class=DataCollector,
    #     visualizer_class=GridVisualizer
    # )
