# -*- coding: utf-8 -*-
__author__ = 'Songmin'

import sys

from Melodie.run import current_scenario
from ..config import REG
from Melodie.db import DB
from Melodie.model import Model
from ..modules.agent import GINIAgent
from ..modules.environment import Environment, GiniEnvironment
from ..modules.data_collector import GiniDataCollector


class GiniModel(Model):

    # def __init__(self, conn, id_scenario):
    #     self.Conn = conn
    #     self.db = None
    #     # scenarioPara = DB().read_DataFrame(REG().Exo_ScenarioPara, self.Conn, ID_Scenario=id_scenario).iloc[0]
    #     scenarioPara = DB().read_DataFrame(REG().Exo_ScenarioPara, self.Conn, ID_Scenario=id_scenario).loc[[0]]
    #     # using 'loc' or 'to_json' instead of 'iloc' is much better because it will not be converted to float64
    #     self.Scenario = GiniScenario()
    #     self.Scenario.set_params(scenarioPara.to_dict('index')[0])

    # def gen_Environment(self):
    #
    #     Env = GiniEnvironment(self.Scenario)
    #
    #     return Env
    #
    # def gen_AgentList(self):
    #
    #     AgentParaDataFrame = DB().read_DataFrame(REG().Gen_AgentPara + "_S" + str(self.Scenario.ID_Scenario), self.Conn)
    #     Agent_list = []
    #     for row in range(0, AgentParaDataFrame.shape[0]):
    #         agent = GINIAgent()
    #         agent.set_params(AgentParaDataFrame.iloc[row])
    #         Agent_list.append(agent)
    #
    #     return Agent_list

    def run(self):
        SimulationPeriods = self.scenario.periods
        Environment = self.environment
        agent_manager = self.setup_agent_manager()
        # dc = GiniDataCollector(self.Conn, self.Scenario.ID_Scenario)
        dc = self.data_collector

        for t in range(0, SimulationPeriods):
            print("ID_Scenario = " + str(self.scenario.id   ) + ", period = " + str(t))
            # print(agent_manager)
            dc.collect(t)
            Environment.go_MoneyProduce(agent_manager)
            Environment.go_MoneyTransfer(agent_manager)
            Environment.calc_WealthAndGini(agent_manager)
            # dc.collect_EnvironmentData(t, Environment)
        dc.save(self.proj_name)

        # dc.save_AgentData()
        # dc.save_EnvironmentData()
