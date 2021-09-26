# import os
# import sqlite3
# from pathlib import Path
#
# from Melodie.scenariomanager import Scenario
#
#
# class CONN:
#
#     def __init__(self):
#         self.ProjectPath = Path(os.path.dirname(__file__))
#         self.DatabasePath = os.path.join(str(self.ProjectPath), "_Database")
#         self.FiguresPath = os.path.join(str(self.ProjectPath), "_Figures")
#         if not os.path.exists(self.DatabasePath):
#             os.mkdir(self.DatabasePath)
#         if not os.path.exists(self.FiguresPath):
#             os.mkdir(self.FiguresPath)
#         self.DBName = "WealthDistribution"
#         self.DBConnection: sqlite3.Connection = self.create_Connection(self.DBName)
#
#     def create_Connection(self, database_name) -> sqlite3.Connection:
#         conn = sqlite3.connect(os.path.join(self.DatabasePath, database_name + ".sqlite"))
#         return conn
#
#
# class REG:
#
#     def __init__(self):
#         # Prefix
#         self.ExogenousData = "Exo_"
#         self.GeneratedData = "Gen_"
#         self.Result = "Res_"
#
#         # Exogenous Table
#         self.Exo_ScenarioPara = self.ExogenousData + "ScenarioPara"
#
#         # Generated Table
#         self.Gen_AgentPara = self.GeneratedData + "AgentPara"
#
#         # Result Table
#         self.Res_AgentPara = self.Result + "AgentPara"
#         self.Res_EnvironmentPara = self.Result + "EnvironmentPara"


# class GiniScenario(Scenario):
#     # params = [
#     #     "ID_Scenario",
#     #     "Periods",
#     #     "AgentNum",
#     #     "AgentAccount_min",
#     #     "AgentAccount_max",
#     #     "AgentProductivity",
#     #     "TradeNum",
#     #     "RichWinProb"]
#     # types = {
#     #     "ID_Scenario": 'INT',
#     #     "Periods": 'INT',
#     #     "AgentNum": 'INT',
#     #     "AgentAccount_min": 'REAL',
#     #     "AgentAccount_max": 'REAL',
#     #     "AgentProductivity": 'REAL',
#     #     "TradeNum": "INTEGER",
#     #     "RichWinProb": 'REAL'}
#
#     def __init__(self, id: int = 1, periods: int = 200, agentNum: int = 100):
#         self.ID_Scenario = id
#         self.Periods = periods
#         self.AgentNum = agentNum
#         self.AgentAccount_min = 0.0
#         self.AgentAccount_max = 100.0
#         self.AgentProductivity = 0.5
#         self.TradeNum = 100
#         self.RichWinProb = 0.2
