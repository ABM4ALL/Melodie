# -*- coding: utf-8 -*-
__author__ = 'Songmin'

from Main._Config.ExParameters import *

from Main.C_Toolkit.a_Doraemon import Doraemon as Dora
from Main.C_Toolkit.b_DatabaseOperator import DatabaseOperator as DB
from Main.C_Toolkit.c_Figure import Figure

class EnvironmentAnalyzer:

    def __init__(self, _ScenarioName):
        self.ScenarioName = _ScenarioName
        self.ScenarioConn = Dora().conn_create(_ScenarioName)

    def WealthAndGini(self):

        EnvironmentResult = DB().read_DataFrame(ScenarioTable_Result_EnvironmentVar, self.ScenarioConn)
        TotalWealth = EnvironmentResult["TotalWealth"].values
        Gini = EnvironmentResult["Gini"].values
        Figure().plot_WealthAndGini(TotalWealth, Gini, ResultFolder, self.ScenarioName)

        return None