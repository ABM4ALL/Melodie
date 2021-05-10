# -*- coding: utf-8 -*-
__author__ = 'Songmin'

from Main.B_Analyzer.a_AgentAnalyzer import AgentAnalyzer
from Main.B_Analyzer.b_EnvironmentAnalyzer import EnvironmentAnalyzer

ScenarioName = "test"
AgentAnalyzer(ScenarioName).AgentWealth(2)
EnvironmentAnalyzer(ScenarioName).WealthAndGini()







