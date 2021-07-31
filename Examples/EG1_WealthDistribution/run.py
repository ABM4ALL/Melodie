from Examples.EG1_WealthDistribution.Config import CONN
from Examples.EG1_WealthDistribution.B_Model.B1_TableGenerator import TableGenerator
from Examples.EG1_WealthDistribution.B_Model.B2_Model import Model
from Examples.EG1_WealthDistribution.B_Model.B3_Analyzer import Analyzer

if __name__ == "__main__":

    db_conn = CONN().DBConnection
    for ID_Scenario in range(1, 2):
        TableGenerator(db_conn, ID_Scenario).run()
        Model(db_conn, ID_Scenario).run()
        Analyzer(db_conn, ID_Scenario).run()

