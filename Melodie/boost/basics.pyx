from typing import Dict, Any
from typing import Tuple, List, Dict, Optional, TYPE_CHECKING

import pandas as pd

from Melodie.basic import MelodieExceptions

if TYPE_CHECKING:
    from Melodie import Model, Scenario

cdef class Element:

    cpdef void set_params(self, dict params) except *:

        """

        :param params: Dict[str, Any]
        :return:
        """
        for paramName, paramValue in params.items():
            assert paramName in self.__dict__.keys(), f"param named {paramName}, value {paramValue} not in Agent.params:{self.__dict__.keys()}"
            setattr(self, paramName, paramValue)




cdef class Environment(Element):
    def __init__(self):
        self.model: Optional['Model'] = None
        self.scenario: Optional['Scenario'] = None

    cpdef void setup(self):
        """
        The setup method of the environment.

        Use `self.scenario` to get the parameters from the scenario.



        :return:
        """
        pass

    cpdef dict to_dict(self, list properties):
        """
        Dump Environment to a plain dict.
        :param properties: List[str]
        :return:
        """
        cdef dict d
        cdef str property 
        if properties is None:
            properties = self.__dict__.keys()
        d = {}
        for property in properties:
            d[property] = self.__dict__[property]
        return d

    cpdef to_dataframe(self, properties: List[str]):
        """
        Dump Environment to a one-row pd.DataFrame
        :param properties:
        :return:
        """
        d = self.to_dict(properties)
        return pd.DataFrame([d])
