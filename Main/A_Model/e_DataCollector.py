# -*- coding: utf-8 -*-
__author__ = 'Songmin'

from Main._Config.ExParameters import *
from Main.C_Toolkit.a_Doraemon import Doraemon as Dora
from Main.C_Toolkit.b_DatabaseOperator import DatabaseOperator as DB

class DataCollector:

    def __init__(self, _ScenarioName):
        self.ScenarioName = _ScenarioName
        self.ScenarioConn = Dora().conn_create(_ScenarioName)
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

        DB().write_DataFrame(self.AgentVar, ScenarioTable_Result_AgentVar, self.AgentVarList, self.ScenarioConn)

        return None

    def save_EnvironmentData(self):

        DB().write_DataFrame(self.EnvironmentVar, ScenarioTable_Result_EnvironmentVar, self.EnvironmentVarList, self.ScenarioConn)

        return None

















