from Melodie.Element import Element
from Melodie.DB import DB


class Scenario(Element):
    pass


class ScenarioManager:

    def __init__(self, conn, id_scenario):
        self.Conn = conn
        self.ID_Scenario = id_scenario
        self.ScenarioPara = DB().read_DataFrame("Exo_ScenarioTable", self.Conn, ID_Scenario=self.ID_Scenario).iloc[0]
        self.ExperimentRun = self.ScenarioPara["ExperimentRun"]

    pass
