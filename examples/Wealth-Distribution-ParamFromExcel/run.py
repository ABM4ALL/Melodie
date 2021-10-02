import os
import sys

sys.path.append("../..")
# Melody package is not available on pip yet, so this example has to import Melody package placed at project root.
# Appending project root to "sys.path" makes Melody package accessible to the interpreter.
# This code will be removed as soon as we release the first distribution onto pip.

from Melodie.config import Config
from WealthDistribution.model.scenario import GiniScenario
from WealthDistribution.modules.agent import GINIAgent
from WealthDistribution.model.model import GiniModel
from WealthDistribution.model.analyzer import Analyzer
from WealthDistribution.modules.environment import GiniEnvironment
from WealthDistribution.modules.data_collector import GiniDataCollector
from Melodie.run import run_with_xls

import time

if __name__ == "__main__":
    # for i in range(100):
    #     # time.sleep(1)
    #     print('+++', end='')
    #     time.sleep(0.1)
    #     if i % 10 == 0:
    #         print('\r', end='')
    # sys.exit()
    run_with_xls(
        GINIAgent,
        GiniEnvironment,
        Config('WealthDistribution', os.path.dirname(__file__),
               parameters_source='from_file',
               parameters_xls_file='params.xlsx',
               static_xls_files=['static1.xlsx', 'static2.xlsx']),
        model_class=GiniModel,
        data_collector_class=GiniDataCollector,
        scenario_class=GiniScenario,
        analyzer_class=Analyzer
    )
