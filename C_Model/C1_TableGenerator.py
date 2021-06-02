# -*- coding: utf-8 -*-
__author__ = 'Songmin'
import numpy as np
from A_Infrastructure.A2_Register import REG
from A_Infrastructure.A3_DB import DB

class TableGenerator:

    def __init__(self, conn, id_scenario):
        self.Conn = conn
        self.ID_Scenario = id_scenario
        self.ScenarioPara = DB().read_DataFrame(REG().Exo_ScenarioPara, self.Conn, ID_Scenario=self.ID_Scenario).iloc[0]

    def gen_AgentParaTable(self):

        AgentNum = int(self.ScenarioPara["AgentNum"])
        IntialAccountMin = self.ScenarioPara["AgentAccount_min"]
        IntialAccountMax = self.ScenarioPara["AgentAccount_max"]
        AgentProductivity = self.ScenarioPara["AgentProductivity"]

        AgentParaTable = np.zeros((AgentNum, 3))
        for agent in range(0, AgentNum):
            AgentParaTable[agent][0] = int(agent + 1)
            AgentParaTable[agent][1] = np.random.randint(IntialAccountMin, IntialAccountMax + 1)
            AgentParaTable[agent][2] = AgentProductivity
        column_name = ["ID_Agent", "InitialAccount", "Productivity"]
        DB().write_DataFrame(AgentParaTable, REG().Gen_AgentPara + "_S" + str(self.ID_Scenario),
                             column_name, self.Conn)

        return None

    def run(self):
        self.gen_AgentParaTable()
