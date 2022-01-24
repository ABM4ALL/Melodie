from typing import Tuple, List, Dict, Optional, TYPE_CHECKING

import pandas as pd

from Melodie.basic import MelodieExceptions

if TYPE_CHECKING:
    from Melodie import Model


class Environment:
    def __init__(self):
        self.model: Optional['Model'] = None
        self.scenario = self.current_scenario()

    def current_scenario(self):
        from Melodie import Scenario
        MelodieExceptions.Assertions.Type('The scenario of self.model', self.model.scenario, Scenario)
        return self.model.scenario

    def setup(self):
        pass

    def to_dict(self, properties: List[str]) -> Dict:
        if properties is None:
            properties = self.__dict__.keys()
        d = {}
        for property in properties:
            d[property] = self.__dict__[property]
        return d

    def to_dataframe(self, properties: List[str]):
        """
        Dump Environment to a one-row pd.DataFrame
        :param properties:
        :return:
        """
        d = self.to_dict(properties)
        return pd.DataFrame([d])
