from typing import Dict, Any
from typing import Tuple, List, Dict, Optional, TYPE_CHECKING

import pandas as pd

from Melodie.basic import MelodieExceptions

from typing import Optional, TYPE_CHECKING

cdef class Element:

    cpdef void set_params(self, dict params) except *:

        """

        :param params: Dict[str, Any]
        :return:
        """
        for paramName, paramValue in params.items():
            assert paramName in self.__dict__.keys(), f"param named {paramName}, value {paramValue} not in Agent.params:{self.__dict__.keys()}"
            setattr(self, paramName, paramValue)





cdef class Agent(Element):
    def __init__(self, agent_id: int):
        self.id = agent_id
        self.scenario = None
        self.model = None


    cpdef void set_params(self, dict params) except *:
        """
        As ``Agent.id`` is a Cython-compiled property, it cannot be modified by ``setattr()`` function. 
        So this method is for overcoming this problem.

        :param params: None
        :return:
        """
        for paramName, paramValue in params.items():
            if paramName=="id":
                self.id = paramValue
            else:
                assert paramName in self.__dict__.keys(), f"param named {paramName}, value {paramValue} not in Agent.params:{self.__dict__.keys()}"
                setattr(self, paramName, paramValue)

    def setup(self):
        """
        This is the initialization method, declare properties here.

        Here, "Declare" is to define properties with an initial value, such as:

        .. code-block:: python
            :linenos:

            class NewAgent(Agent)
                def setup(self):
                    self.int_property = 0  # int property
                    self.float_property = 0.0  # float property
                    self.str_property = ""  # string property


        It is also fine to define properties with complex data structure such as dict/list/set, but the values in the
        complex data structure is hard to be recorded by the `DataCollector`


        This method is executed at the end of the `__init__` method of the corresponding agent container.

        :return:
        """
        pass

    def __repr__(self) -> str:
        d = {k: v for k, v in self.__dict__.items() if
             not k.startswith("_")}
        d['id'] = self.id
        return "<%s %s>" % (self.__class__.__name__, d)


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
