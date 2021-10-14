# -*- coding: utf-8 -*-
__author__ = 'Songmin'

import os
import sys

sys.path.append("../..")
# Melody package is not available on pip yet, so this example has to import Melody package placed at project root.
# Appending project root to "sys.path" makes Melody package accessible to the interpreter.
# This code will be removed as soon as we release the first distribution onto pip.

from Melodie.config import Config
from TertiaryModel.model.scenario import TertiaryScenarioManager
from TertiaryModel.modules.agent import TertiaryAgent
from TertiaryModel.model.table_generator import TertiaryTableGenerator
from TertiaryModel.model.model import TertiaryModel
from TertiaryModel.model.analyzer import Analyzer
from TertiaryModel.modules.environment import TertiaryEnvironment
from TertiaryModel.modules.data_collector import TertiaryDataCollector
from Melodie.run import run

if __name__ == "__main__":
    print("hello")
    run(
        TertiaryAgent,
        TertiaryEnvironment,
        Config('TertiaryModel', os.path.dirname(__file__)),
        model_class=TertiaryModel,
        data_collector_class=TertiaryDataCollector,
        scenario_manager_class=TertiaryScenarioManager,
        table_generator_class=TertiaryTableGenerator,
        analyzer_class=Analyzer
    )
