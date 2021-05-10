# -*- coding: utf-8 -*-
__author__ = 'Songmin'

from Main._Config.ExParameters import *

from Main.A_Model.b_ScenarioSetup import ScenarioSetup
from Main.A_Model.c_Environment import Environment
from Main.A_Model.d_Agent import Agent
from Main.A_Model.e_DataCollector import DataCollector

from Main.C_Toolkit.a_Doraemon import Doraemon as Dora
from Main.C_Toolkit.b_DatabaseOperator import DatabaseOperator as DB

class Model:

    def __init__(self, _ScenarioName):
        self.ScenarioName = _ScenarioName
        self.ScenarioConn = Dora().conn_create(self.ScenarioName)

    def gen_Environment(self):

        EnvironmentDataFrame = DB().read_DataFrame(ScenarioTable_EnvironmentPara, self.ScenarioConn)
        EnvironmentAgent = Environment(EnvironmentDataFrame)

        return EnvironmentAgent

    def gen_AgentList(self):

        AgentParaDataFrame = DB().read_DataFrame(ScenarioTable_AgentParaTable, self.ScenarioConn)
        Agent_list = []
        for row in range(0, AgentParaDataFrame.shape[0]):
            agent = Agent(AgentParaDataFrame.iloc[row])
            Agent_list.append(agent)

        return Agent_list

    def run(self):

        ScenarioSetup(self.ScenarioName).run()
        SystemPara = DB().read_DataFrame(ScenarioTable_SystemPara, self.ScenarioConn)
        SimulationPeriods = SystemPara.iloc[0]["Periods"]
        Environment = self.gen_Environment()
        AgentList = self.gen_AgentList()
        DC = DataCollector(self.ScenarioName)

        for t in range(0, SimulationPeriods):
            print(t)
            DC.collect_AgentData(t, AgentList)
            Environment.go_MoneyProduce(AgentList)
            Environment.go_MoneyTransfer(AgentList)
            Environment.calc_WealthAndGini(AgentList)
            DC.collect_EnvironmentData(t, Environment)

        DC.save_AgentData()
        DC.save_EnvironmentData()


