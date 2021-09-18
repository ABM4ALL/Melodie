from typing import List

from Melodie.element import Element
import pandas as pd


class Scenario(Element):
    def __init__(self, id_scenario: int = 0):
        super().__init__()
        self.id = id_scenario
        self.setup()

    def setup(self):
        pass

    def toDict(self):
        # print(self.__dict__)
        d = {}
        for k in self.params:
            d[k] = self.__dict__[k]
        return d

    def __repr__(self):
        return str(self.__dict__)


class ScenarioManager:

    # def __init__(self, conn, id_scenario):
    #     self.Conn = conn
    #     self.ID_Scenario = id_scenario
    def __init__(self):
        self._scenarios = self.gen_scenarios()

    def gen_scenarios(self) -> List[Scenario]:
        """
        The method to generate scenarios.
        :return:
        """
        pass
        # self.ScenarioPara = DB().read_DataFrame("Exo_ScenarioTable", self.Conn, ID_Scenario=self.ID_Scenario).iloc[0]
        # self.ExperimentRun = self.ScenarioPara["ExperimentRun"]

    def _gen_scenarios(self) -> List[Scenario]:
        self.gen_scenarios()

    def to_dataframe(self) -> pd.DataFrame:
        """

        :return:
        """
        l = []
        for scenario in self._scenarios:
            l.append(scenario.__dict__)
        df = pd.DataFrame(l)
        return df
