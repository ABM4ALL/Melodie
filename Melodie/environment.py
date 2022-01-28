from typing import Tuple, List, Dict, Optional, TYPE_CHECKING

import pandas as pd

from Melodie.basic import MelodieExceptions
from Melodie.element import Element

if TYPE_CHECKING:
    from Melodie import Model, Scenario


class Environment(Element):
    def __init__(self):
        self.model: Optional['Model'] = None
        self.scenario: Optional['Scenario'] = None

    def current_scenario(self):
        """
        Get the current scenario.
        :return:
        """
        from Melodie import Scenario
        MelodieExceptions.Assertions.Type('The scenario of self.model', self.model.scenario, Scenario)
        return self.model.scenario

    def setup(self):
        """
        The setup method of the environment.

        Use `self.current_scenario()` to get the parameters from the scenario.

        Unlike `Agent`, Environment does not have a `post_setup` method because the parameters could be extracted
        directly from the scenario.

        :return:
        """
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
