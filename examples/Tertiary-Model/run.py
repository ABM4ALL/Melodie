import os
import sys

sys.path.append("../..")
# Melody package is not available on pip yet, so this example has to import Melody package placed at project root.
# Appending project root to "sys.path" makes Melody package accessible to the interpreter.
# This code will be removed as soon as we release the first distribution onto pip.

from Melodie.config import Config
from TertiaryModel.model.scenario import GiniScenarioManager
from TertiaryModel.modules.agent import TertiaryAgent
from TertiaryModel.model.table_generator import GiniTableGenerator
from TertiaryModel.model.model import GiniModel
from TertiaryModel.model.analyzer import Analyzer
from TertiaryModel.modules.environment import TertiaryEnvironment
from TertiaryModel.modules.data_collector import GiniDataCollector
from Melodie.run import run

if __name__ == "__main__":
    print("hello")
    # run(
    #     TertiaryAgent,
    #     TertiaryEnvironment,
    #     Config('TertiaryModel', os.path.dirname(__file__)),
    #     model_class=GiniModel,
    #     data_collector_class=GiniDataCollector,
    #     scenario_manager_class=GiniScenarioManager,
    #     table_generator_class=GiniTableGenerator,
    #     analyzer_class=Analyzer
    # )
