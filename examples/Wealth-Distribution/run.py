import sys

sys.path.append("../..")
# Melody package is not available on pip yet, so this example has to import Melody package placed at project root.
# Appending project root to "sys.path" makes Melody package accessible to the interpreter.
# This code will be removed as soon as we release the first distribution onto pip.

from WealthDistribution.Config import CONN, GiniScenario
from WealthDistribution.A_Class.A1_Agent import GINIAgent
from WealthDistribution.B_Model.B1_TableGenerator import TableGenerator
from WealthDistribution.B_Model.B2_Model import Model
from WealthDistribution.B_Model.B3_Analyzer import Analyzer

if __name__ == "__main__":

    db_conn = CONN().DBConnection
    for ID_Scenario in range(1, 2):
        scenario = GiniScenario(ID_Scenario, 200, 100)  # scenario is a new class
        TableGenerator(db_conn, scenario, GINIAgent).run()
        Model(db_conn, ID_Scenario).run()
        Analyzer(db_conn, ID_Scenario).run()
