import sys

sys.path.append("../..")
# Melody package is not available on pip yet, so this example has to import Melody package placed at project root.
# Appending project root to "sys.path" makes Melody package accessible to the interpreter.
# This code will be removed as soon as we release the first distribution onto pip.

from WealthDistribution.model.scenario import GiniScenarioManager
from WealthDistribution.modules.agent import GINIAgent
from WealthDistribution.model.table_generator import GiniTableGenerator
from WealthDistribution.model.model import GiniModel
from WealthDistribution.model.analyzer import Analyzer
from WealthDistribution.modules.environment import GiniEnvironment
from WealthDistribution.modules.data_collector import GiniDataCollector
from Melodie.run import run

if __name__ == "__main__":
    run('WealthDistribution',GINIAgent, GiniEnvironment, model_class=GiniModel, data_collector_class=GiniDataCollector,
        scenario_manager_class=GiniScenarioManager, table_generator_class=GiniTableGenerator)
    # db_conn = CONN().DBConnection
    # for ID_Scenario in range(1, 2):
    #     scenario = GiniScenario(ID_Scenario, 200, 100)  # scenario is a new class
    #     TableGenerator(db_conn, scenario, GINIAgent).run()
    #     Model(db_conn, ID_Scenario).run()
    #     Analyzer(db_conn, ID_Scenario).run()
