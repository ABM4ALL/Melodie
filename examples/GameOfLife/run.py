import sys

sys.path.append("../..")
# Melody package is not available on pip yet, so this example has to import Melody package placed at project root.
# Appending project root to "sys.path" makes Melody package accessible to the interpreter.
# This code will be removed as soon as we release the first distribution onto pip.

from model.scenario import GameOfLifeScenario
from model.model import GameOfLifeModel
from model.simulator import GameOfLifeSimulator
from config import config
from model.df_loader import GameOfLifeDataFrameLoader
from Melodie import run_profile

if __name__ == "__main__":
    simulator = GameOfLifeSimulator(config, GameOfLifeScenario, GameOfLifeModel, GameOfLifeDataFrameLoader)

    """
    Run the model with dataframe_loader
    """

    run_profile(simulator.run_visual)
