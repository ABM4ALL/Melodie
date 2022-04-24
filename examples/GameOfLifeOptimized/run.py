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
from Melodie import run_profile
from config import config
from model.df_loader import GameOfLifeDataFrameLoader

if __name__ == "__main__":
    simulator = FuncSimulator(config, GameOfLifeScenario, GameOfLifeModel, GameOfLifeDataFrameLoader)

    """
    Run the model with dataframe_loader
    """
    run_profile(simulator.run)

    # dataframe_loader.run_visual(
    #     # agent_class=None,
    #     # environment_class=GameOfLifeEnvironment,
    #     config=config,
    #     model_class=GameOfLifeModel,
    #     scenario_cls=GameOfLifeScenario,
    #     # data_collector_class=DataCollector,
    #     visualizer_class=GridVisualizer
    # )