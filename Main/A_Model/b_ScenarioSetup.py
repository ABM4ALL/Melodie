# -*- coding: utf-8 -*-
__author__ = 'Songmin'

from Main._Config.ExPackages import *
from Main._Config.ExParameters import *
from Main.C_Toolkit.a_Doraemon import Doraemon
from Main.C_Toolkit.b_DatabaseOperator import DatabaseOperator as DB

class ScenarioSetup:

    def __init__(self, _ScenarioName):
        self.RootConn = Doraemon().conn_create("root")
        self.ScenarioConn = Doraemon().conn_create(_ScenarioName)

    def init_ScenarioDatabase(self):

        # Copy tables from root to scenario
        DB().copy_DataFrame(RootTable_AgentParaRoot, self.RootConn, ScenarioTable_AgentParaRoot, self.ScenarioConn)
        DB().copy_DataFrame(RootTable_EnvironmentParaRoot, self.RootConn, ScenarioTable_EnvironmentPara, self.ScenarioConn)
        DB().copy_DataFrame(RootTable_SystemParaRoot, self.RootConn, ScenarioTable_SystemPara, self.ScenarioConn)

        # Setup the AgentParaTable
        AgentParaRoot = DB().read_DataFrame(ScenarioTable_AgentParaRoot, self.ScenarioConn)
        IntialAccountMin = AgentParaRoot.iloc[0]["Min"]
        IntialAccountMax = AgentParaRoot.iloc[0]["Max"]
        AgentProductivity = AgentParaRoot.iloc[0]["Productivity"]

        SystemPara = DB().read_DataFrame(ScenarioTable_SystemPara, self.ScenarioConn)
        AgentNum = int(SystemPara.iloc[0]["AgentNum"])

        AgentParaTable = np.zeros((AgentNum, 3))
        for agent in range(0, AgentNum):
            AgentParaTable[agent][0] = agent
            AgentParaTable[agent][1] = np.random.randint(IntialAccountMin, IntialAccountMax + 1)
            AgentParaTable[agent][2] = AgentProductivity
        column_name = ["ID", "InitialAccount", "Productivity"]
        DB().write_DataFrame(AgentParaTable, ScenarioTable_AgentParaTable,
                             column_name, self.ScenarioConn)

        return None

    def run(self):
        self.init_ScenarioDatabase()
