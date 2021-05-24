# -*- coding: utf-8 -*-
__author__ = 'Songmin'

from A_Infrastructure.A2_Register import REG
from A_Infrastructure.A3_DB import DB
from B_Classes.B1_Agent import Agent
from B_Classes.B2_Environment import Environment
from B_Classes.B3_DataCollector import DataCollector

class Model:

    def __init__(self, conn, id_scenario):
        self.Conn = conn
        self.ID_Scenario = id_scenario

    def gen_Environment(self):

        EnvironmentDataFrame = DB().read_DataFrame(REG().Exo_ScenarioPara, self.Conn, ID_Scenario=self.ID_Scenario)
        EnvironmentAgent = Environment(EnvironmentDataFrame)

        return EnvironmentAgent

    def gen_AgentList(self):

        AgentParaDataFrame = DB().read_DataFrame(REG().Gen_AgentPara + "_S" + str(self.ID_Scenario), self.Conn)
        Agent_list = []
        for row in range(0, AgentParaDataFrame.shape[0]):
            agent = Agent(AgentParaDataFrame.iloc[row])
            Agent_list.append(agent)

        return Agent_list

    def run(self):

        SystemPara = DB().read_DataFrame(REG().Exo_SystemPara, self.Conn)
        SimulationPeriods = SystemPara.iloc[0]["Periods"]
        Environment = self.gen_Environment()
        AgentList = self.gen_AgentList()
        DC = DataCollector(self.Conn, self.ID_Scenario)

        for t in range(0, SimulationPeriods):
            print("ID_Scenario = " + str(self.ID_Scenario) + ", period = " + str(t))
            DC.collect_AgentData(t, AgentList)
            Environment.go_MoneyProduce(AgentList)
            Environment.go_MoneyTransfer(AgentList)
            Environment.calc_WealthAndGini(AgentList)
            DC.collect_EnvironmentData(t, Environment)

        DC.save_AgentData()
        DC.save_EnvironmentData()


