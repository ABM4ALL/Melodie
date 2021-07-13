# -*- coding: utf-8 -*-
__author__ = 'Songmin'

from EG1_WealthDistribution.Config import REG
from _Melodie.DB import DB

class DataCollector:

    def __init__(self, conn, id_scenario):
        self.Conn = conn
        self.ID_Scenario = id_scenario
        self.AgentVar_Column = {"Period": "INTEGER",
                                "ID": "INTEGER",
                                "Account": "REAL"}
        self.AgentVar_ValueList = []
        self.EnvironmentVar_Column = {"Period": "INTEGER",
                                      "TotalWealth": "REAL",
                                      "Gini": "REAL"}
        self.EnvironmentVar_ValueList = []

    def collect_AgentData(self, period, AgentList):

        for agent in AgentList:
            self.AgentVar_ValueList.append([period + 1, agent.ID, agent.Account])

        return None

    def collect_EnvironmentData(self, period, Environment):

        self.EnvironmentVar_ValueList.append([period + 1, Environment.TotalWealth, Environment.Gini])

        return None

    def save_AgentData(self):

        DB().write_DataFrame(self.AgentVar_ValueList, REG().Res_AgentPara + "_S" + str(self.ID_Scenario),
                             self.AgentVar_Column.keys(), self.Conn, dtype=self.AgentVar_Column)

        return None

    def save_EnvironmentData(self):

        DB().write_DataFrame(self.EnvironmentVar_ValueList, REG().Res_EnvironmentPara + "_S" + str(self.ID_Scenario),
                             self.EnvironmentVar_Column.keys(), self.Conn, dtype=self.EnvironmentVar_Column)

        return None

















