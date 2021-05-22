# -*- coding: utf-8 -*-
__author__ = 'Songmin'

from A_Infrastructure.A1_Constants import CONS
from A_Infrastructure.A2_Register import REG
from A_Infrastructure.A3_DB import DB
from A_Infrastructure.A4_Figure import Figure

class Analyzer:

    def __init__(self, conn, id_scenario):
        self.Conn = conn
        self.ID_Scenario = id_scenario

    def analyze_AgentWealth(self, id_agent):

        AgentResult = DB().read_DataFrame(REG().Res_AgentPara + "_S" + str(self.ID_Scenario), self.Conn)
        AgentWealth = AgentResult.loc[AgentResult["ID"] == id_agent]["Account"].values
        Figure().plot_AgentWealth(AgentWealth, id_agent, CONS().FiguresPath, self.ID_Scenario)

        return None

    def analyze_WealthAndGini(self):

        EnvironmentResult = DB().read_DataFrame(REG().Res_EnvironmentPara + "_S" + str(self.ID_Scenario), self.Conn)
        TotalWealth = EnvironmentResult["TotalWealth"].values
        Gini = EnvironmentResult["Gini"].values
        Figure().plot_WealthAndGini(TotalWealth, Gini, CONS().FiguresPath, self.ID_Scenario)

        return None

    def run(self):
        self.analyze_AgentWealth(1)
        self.analyze_WealthAndGini()

