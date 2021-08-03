# -*- coding: utf-8 -*-
__author__ = 'Songmin'
import numpy as np
from examples.WealthDistribution.Config import REG
from _Melodie.DB import DB

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
        data_column = {"ID_Agent": "INTEGER",
                       "InitialAccount": "REAL",
                       "Productivity": "REAL"}
        DB().write_DataFrame(AgentParaTable, REG().Gen_AgentPara + "_S" + str(self.ID_Scenario),
                             data_column.keys(), self.Conn, dtype=data_column)

        return None

    def run(self):
        self.gen_AgentParaTable()
