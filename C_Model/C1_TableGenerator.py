# -*- coding: utf-8 -*-
__author__ = 'Songmin'
import numpy as np
from A_Infrastructure.A2_Register import REG
from A_Infrastructure.A3_DB import DB

class TableGenerator:

    def __init__(self, conn, id_scenario):
        self.Conn = conn
        self.ID_Scenario = id_scenario

    def gen_AgentParaTable(self):

        AgentParaRoot = DB().read_DataFrame(REG().Exo_AgentPara, self.Conn)
        IntialAccountMin = AgentParaRoot.iloc[0]["Min"]
        IntialAccountMax = AgentParaRoot.iloc[0]["Max"]
        AgentProductivity = AgentParaRoot.iloc[0]["Productivity"]

        SystemPara = DB().read_DataFrame(REG().Exo_SystemPara, self.Conn)
        AgentNum = int(SystemPara.iloc[0]["AgentNum"])

        AgentParaTable = np.zeros((AgentNum, 3))
        for agent in range(0, AgentNum):
            AgentParaTable[agent][0] = int(agent + 1)
            AgentParaTable[agent][1] = np.random.randint(IntialAccountMin, IntialAccountMax + 1)
            AgentParaTable[agent][2] = AgentProductivity
        column_name = ["ID_Agent", "InitialAccount", "Productivity"]
        DB().write_DataFrame(AgentParaTable, REG().Gen_AgentParaTable + "_S" + str(self.ID_Scenario),
                             column_name, self.Conn)

        return None

    def run(self):
        self.gen_AgentParaTable()
