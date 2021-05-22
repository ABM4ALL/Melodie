
class REG:

    def __init__(self):

        # Prefix
        self.ExogenousData = "Exo_"
        self.GeneratedData = "Gen_"
        self.Result = "Res_"

        # Exogenous Table
        self.Exo_SystemPara = self.ExogenousData + "SystemPara"
        self.Exo_AgentPara = self.ExogenousData + "AgentPara"
        self.Exo_ScenarioPara = self.ExogenousData + "ScenarioPara"

        # Generated Table
        self.Gen_AgentParaTable = self.GeneratedData + "AgentParaTable"

        # Result Table
        self.Res_AgentPara = self.Result + "AgentPara"
        self.Res_EnvironmentPara = self.Result + "EnvironmentPara"












