import os
import sys

sys.path.append("../..")
# Melody package is not available on pip yet, so this example has to import Melody package placed at project root.
# Appending project root to "sys.path" makes Melody package accessible to the interpreter.
# This code will be removed as soon as we release the first distribution onto pip.

from Melodie.config import Config
from WealthDistribution.model.scenario import GiniScenarioManager
from WealthDistribution.modules.agent import GINIAgent
from WealthDistribution.model.table_generator import GiniTableGenerator
from WealthDistribution.model.model import GiniModel
from WealthDistribution.model.analyzer import Analyzer
from WealthDistribution.modules.environment import GiniEnvironment
from WealthDistribution.modules.data_collector import GiniDataCollector
from Melodie.run import run_with_xls

if __name__ == "__main__":
    run_with_xls(
        GINIAgent,
        GiniEnvironment,
        Config('WealthDistribution', os.path.dirname(__file__)),
        model_class=GiniModel,
        data_collector_class=GiniDataCollector,
        scenario_manager_class=GiniScenarioManager,
        table_generator_class=GiniTableGenerator,
        analyzer_class=Analyzer
    )
#     test
