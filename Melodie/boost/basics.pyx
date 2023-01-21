# cython:language_level=3
from typing import Dict, Any
from typing import Tuple, List, Dict, Optional, TYPE_CHECKING

import pandas as pd

from MelodieInfra import MelodieExceptions

from typing import Optional, TYPE_CHECKING

cdef class Element:

    cpdef void set_params(self, dict params) except *:

        """

        :param params: Dict[str, Any]
        :return:
        """
        for paramName, paramValue in params.items():
            assert hasattr(self, paramName), f"param named {paramName}, value {paramValue} not in Agent.params"
            setattr(self, paramName, paramValue)





cdef class Agent(Element):
    """
    Base class for Agent.

    """
    def __init__(self, agent_id: int):
        """

        :param agent_id: The ``id`` of agent. For the agents of same class,
            it should be unique.
        """
        self.id = agent_id
        self.scenario = None
        self.model = None

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
        if not hasattr(self, '__dict__'):
            return super().__repr__()
        d = {k: v for k, v in self.__dict__.items() if
             not k.startswith("_")}
        d['id'] = self.id
        return "<%s %s>" % (self.__class__.__name__, d)

    cpdef dict to_dict(self, list properties) except *:
        """
        Dump Agent to a plain dict.

        :param properties: List[str]
        :return:
        """
        cdef dict d
        cdef str property
        d = {"id": self.id}
        for property in properties:
            attr = getattr(self, property)
            if isinstance(attr, (int, float, bool, str)):
                d[property] = attr
            else:
                d[property] = f"<Type {type(attr)}>"
        return d

    def get_style(self):
        raise NotImplementedError("Method `get_style` should be inherited if visualizer is implemented!")

cdef class Environment(Element):
    """
    Environment coordinates the agents' decision-making and interaction processes and stores the macro-level variables.
    
    """
    def __init__(self):
        """
        No parameter involved in this class

        """
        self.model: Optional['Model'] = None
        self.scenario: Optional['Scenario'] = None

    def setup(self):
        """
        The setup method of the environment.

        Use `self.scenario` to get the parameters from the scenario.



        :return:
        """
        pass

    cpdef dict to_dict(self, list properties):
        """
        Dump environment properties declared in ``properties`` to a plain dict.

        :param properties: List[str], property names to dump
        :return: A dict, keys are environment property names, while value are property values.
        """
        cdef dict d
        cdef str property 
        d = {}
        for property in properties:
            d[property] = getattr(self, property)
        return d

    cpdef to_dataframe(self, properties: List[str]):
        """
        Dump Environment to a one-row pd.DataFrame

        :param properties:
        :return:
        """
        d = self.to_dict(properties)
        return pd.DataFrame([d])

    def _setup(self):
        self.setup()