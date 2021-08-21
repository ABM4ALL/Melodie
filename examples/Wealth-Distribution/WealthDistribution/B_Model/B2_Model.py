# -*- coding: utf-8 -*-
__author__ = 'Songmin'

import pandas.io.sql

from ..Config import REG
from Melodie.DB import DB
from ..A_Class.A1_Agent import Agent
from ..A_Class.A2_Environment import Environment
from ..A_Class.A3_DataCollector import DataCollector


class Model:

    def __init__(self, conn, id_scenario):
        self.Conn = conn
        self.ID_Scenario = id_scenario
        self.ScenarioPara = DB().read_DataFrame(REG().Exo_ScenarioPara, self.Conn, ID_Scenario=self.ID_Scenario).iloc[0]

    def gen_Environment(self):

        Env = Environment(self.ScenarioPara)

        return Env

    def gen_AgentList(self):

        AgentParaDataFrame = DB().read_DataFrame(REG().Gen_AgentPara + "_S" + str(self.ID_Scenario), self.Conn)
        Agent_list = []
        for row in range(0, AgentParaDataFrame.shape[0]):
            agent = Agent(AgentParaDataFrame.iloc[row])
            Agent_list.append(agent)

        return Agent_list

    def run(self):

        SimulationPeriods = int(self.ScenarioPara["Periods"])
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
