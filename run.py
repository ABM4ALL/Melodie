
from A_Infrastructure.A1_Constants import CONS
from A_Infrastructure.A3_DB import DB
from C_Model.C1_TableGenerator import TableGenerator
from C_Model.C2_Model import Model
from C_Model.C3_Analyzer import Analyzer

if __name__ == "__main__":

    CONN = DB().create_Connection(CONS().RootDB)
    for ID_Scenario in range(1, 7):
        TableGenerator(CONN, ID_Scenario).run()
        Model(CONN, ID_Scenario).run()
        Analyzer(CONN, ID_Scenario).run()


