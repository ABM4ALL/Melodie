import os
import sqlite3
from pathlib import Path


class CONN:

    def __init__(self):
        self.ProjectPath = Path(os.path.dirname(__file__))
        self.DatabasePath = os.path.join(str(self.ProjectPath), "_Database")
        self.FiguresPath = os.path.join(str(self.ProjectPath), "_Figures")
        if not os.path.exists(self.DatabasePath):
            os.mkdir(self.DatabasePath)
        if not os.path.exists(self.FiguresPath):
            os.mkdir(self.FiguresPath)
        self.DBName = "WealthDistribution"
        self.DBConnection: sqlite3.Connection = self.create_Connection(self.DBName)

    def create_Connection(self, database_name) -> sqlite3.Connection:
        conn = sqlite3.connect(os.path.join(self.DatabasePath, database_name + ".sqlite"))
        return conn


class REG:

    def __init__(self):
        # Prefix
        self.ExogenousData = "Exo_"
        self.GeneratedData = "Gen_"
        self.Result = "Res_"

        # Exogenous Table
        self.Exo_ScenarioPara = self.ExogenousData + "ScenarioPara"

        # Generated Table
        self.Gen_AgentPara = self.GeneratedData + "AgentPara"

        # Result Table
        self.Res_AgentPara = self.Result + "AgentPara"
        self.Res_EnvironmentPara = self.Result + "EnvironmentPara"
