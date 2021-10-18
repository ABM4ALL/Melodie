import os
import sys

sys.path.append("../..")
# Melody package is not available on pip yet, so this example has to import Melody package placed at project root.
# Appending project root to "sys.path" makes Melody package accessible to the interpreter.
# This code will be removed as soon as we release the first distribution onto pip.
from model.agent import GINIAgent
from model.environment import GiniEnvironment
from model.scenario import GiniScenario
from model.data_collector import GiniDataCollector
from model.model import GiniModel
from model.simulator import GiniSimulator
from analyzer.analyzer import Analyzer
# from Melodie import Simulator
from Melodie.run import run, run_new

from config import config

if __name__ == "__main__":
    simulator = GiniSimulator()
    simulator.run(
        GINIAgent,
        GiniEnvironment,
        config,
        # Config('WealthDistribution', os.path.dirname(__file__),
        #        parameters_source='from_file',
        #        parameters_xls_file='params.xlsx',
        #        static_xls_files=['static1.xlsx', 'static2.xlsx']),
        model_class=GiniModel,
        data_collector_class=GiniDataCollector,
        scenario_class=GiniScenario,
        analyzer_class=Analyzer
    )

    simulator.run_parallel(
        GINIAgent,
        GiniEnvironment,
        config,
        # Config('WealthDistribution', os.path.dirname(__file__),
        #        parameters_source='from_file',
        #        parameters_xls_file='params.xlsx',
        #        static_xls_files=['static1.xlsx', 'static2.xlsx']),
        model_class=GiniModel,
        data_collector_class=GiniDataCollector,
        scenario_class=GiniScenario,
        analyzer_class=Analyzer
    )
