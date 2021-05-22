# -*- coding: utf-8 -*-
__author__ = 'Songmin'

from A_Infrastructure.A2_Register import REG
from A_Infrastructure.A3_DB import DB

class DataCollector:

    def __init__(self, conn, id_scenario):
        self.Conn = conn
        self.ID_Scenario = id_scenario
        self.AgentVarList = ["Period", "ID", "Account"]
        self.AgentVar = []
        self.EnvironmentVarList = ["Period", "TotalWealth", "Gini"]
        self.EnvironmentVar = []

    def collect_AgentData(self, period, AgentList):

        for agent in AgentList:
            self.AgentVar.append([period, agent.ID, agent.Account])

        return None

    def collect_EnvironmentData(self, period, Environment):

        self.EnvironmentVar.append([period, Environment.TotalWealth, Environment.Gini])

        return None

    def save_AgentData(self):

        DB().write_DataFrame(self.AgentVar, REG().Res_AgentPara + "_S" + str(self.ID_Scenario), self.AgentVarList, self.Conn)

        return None

    def save_EnvironmentData(self):

        DB().write_DataFrame(self.EnvironmentVar, REG().Res_EnvironmentPara + "_S" + str(self.ID_Scenario), self.EnvironmentVarList, self.Conn)

        return None

















