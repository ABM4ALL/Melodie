# -*- coding: utf-8 -*-
__author__ = 'Songmin'

import sys

from ..Config import REG, GiniScenario
from Melodie.DB import DB
from ..A_Class.A1_Agent import GINIAgent
from ..A_Class.A2_Environment import Environment
from ..A_Class.A3_DataCollector import DataCollector


class Model:

    def __init__(self, conn, id_scenario):
        self.Conn = conn
        # scenarioPara = DB().read_DataFrame(REG().Exo_ScenarioPara, self.Conn, ID_Scenario=id_scenario).iloc[0]
        scenarioPara = DB().read_DataFrame(REG().Exo_ScenarioPara, self.Conn, ID_Scenario=id_scenario).loc[[0]]
        # using 'loc' or 'to_json' instead of 'iloc' is much better because it will not be converted to float64
        self.Scenario = GiniScenario()
        self.Scenario.setup(scenarioPara.to_dict('index')[0])


    def gen_Environment(self):

        Env = Environment(self.Scenario)

        return Env

    def gen_AgentList(self):

        AgentParaDataFrame = DB().read_DataFrame(REG().Gen_AgentPara + "_S" + str(self.Scenario.ID_Scenario), self.Conn)
        Agent_list = []
        for row in range(0, AgentParaDataFrame.shape[0]):
            agent = GINIAgent()
            agent.setup(AgentParaDataFrame.iloc[row])
            Agent_list.append(agent)

        return Agent_list

    def run(self):

        SimulationPeriods = self.Scenario.Periods
        Environment = self.gen_Environment()
        AgentList = self.gen_AgentList()
        DC = DataCollector(self.Conn, self.Scenario.ID_Scenario)

        for t in range(0, SimulationPeriods):
            print("ID_Scenario = " + str(self.Scenario.ID_Scenario) + ", period = " + str(t))
            DC.collect_AgentData(t, AgentList)
            Environment.go_MoneyProduce(AgentList)
            Environment.go_MoneyTransfer(AgentList)
            Environment.calc_WealthAndGini(AgentList)
            DC.collect_EnvironmentData(t, Environment)

        DC.save_AgentData()
        DC.save_EnvironmentData()
