from typing import Any, Optional, TYPE_CHECKING, Dict, List

import pandas as pd

if TYPE_CHECKING:
    from Melodie.model import Model
    from Melodie.scenario_manager import Scenario


class Element:

    def set_params(self, params: Dict[str, Any]):
        """

        :param params:
        :return:
        """
        for paramName, paramValue in params.items():
            assert paramName in self.__dict__.keys(
            ), f"param named {paramName}, value {paramValue} not in Agent.params:{self.__dict__.keys()}"
            setattr(self, paramName, paramValue)


class Agent(Element):
    def __init__(self, agent_id: int):
        self.id = agent_id
        self.scenario: Optional['Scenario'] = None
        self.model: Optional['Model'] = None

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
        return "<%s %s>" % (self.__class__.__name__, d)

    def set_params(self, params: Dict[str, Any]):
        """

        :param params:
        :return:
        """
        for paramName, paramValue in params.items():
            if paramName == 'id':
                self.id = paramValue
            else:
                assert paramName in self.__dict__.keys(
                ), f"param named {paramName}, value {paramValue} not in Agent.params:{self.__dict__.keys()}"
                setattr(self, paramName, paramValue)


class Environment(Element):
    def __init__(self):
        self.model: Optional['Model'] = None
        self.scenario: Optional['Scenario'] = None

    def setup(self) -> None:
        """
        The setup method of the environment.

        Use `self.scenario` to get the parameters from the scenario.



        :return:
        """
        pass

    def to_dict(self, properties: List[str]) -> Dict:
        """
        Dump Environment to a plain dict.
        :param properties:
        :return:
        """

    def to_dataframe(self, properties: List[str]) -> pd.DataFrame:
        """
        Dump Environment to a one-row pd.DataFrame
        :param properties:
        :return:
        """
