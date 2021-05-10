# -*- coding: utf-8 -*-
__author__ = 'Songmin'

from Main._Config.ExParameters import *

from Main.C_Toolkit.a_Doraemon import Doraemon as Dora
from Main.C_Toolkit.b_DatabaseOperator import DatabaseOperator as DB
from Main.C_Toolkit.c_Figure import Figure

class AgentAnalyzer:

    def __init__(self, _ScenarioName):
        self.ScenarioName = _ScenarioName
        self.ScenarioConn = Dora().conn_create(_ScenarioName)

    def AgentWealth(self, AgentID):

        AgentResult = DB().read_DataFrame(ScenarioTable_Result_AgentVar, self.ScenarioConn)
        AgentWealth = AgentResult.loc[AgentResult["ID"] == AgentID]["Account"].values
        Figure().plot_AgentWealth(AgentWealth, AgentID, ResultFolder, self.ScenarioName)

        return None
