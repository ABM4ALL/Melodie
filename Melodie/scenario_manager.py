import logging
from typing import List, Optional, Union, TYPE_CHECKING

from Melodie.element import Element
from .basic.exceptions import MelodieExceptions
import pandas as pd

if TYPE_CHECKING:
    from Melodie import Calibrator, Simulator
logger = logging.getLogger(__name__)


class Scenario(Element):
    class BaseParameter:
        def __init__(self, name, type, init):
            self.name = name
            self.type = type
            self.init = init

        def to_dict(self):
            return self.__dict__

        def __repr__(self):
            return f"<class {self.__class__.__name__}, name {self.name}, type {self.type}>"

    class NumberParameter(BaseParameter):
        def __init__(self, name, init_value: Union[int, float], min_val: Optional[Union[int, float]] = None,
                     max_val: Optional[Union[int, float]] = None,
                     step: Optional[Union[int, float]] = None):
            super().__init__(name, "number", init_value)
            if min_val is None or max_val is None or step is None:
                raise NotImplementedError("This version of melodie does not support free bound or step yet")
            assert isinstance(init_value, (int, float))
            assert isinstance(max_val, (int, float))
            assert isinstance(min_val, (int, float))
            assert isinstance(step, (int, float))
            self.min = min_val
            self.max = max_val
            self.step = step
        # def __setattr__(self, key, value):
        #     if hasattr(self, key):
        #         assert key in
    class SelectionParameter(BaseParameter):
        def __init__(self, name, init_value: Union[int, str, bool], selections: List[Union[int, str, bool]]):
            super().__init__(name, "selection", init_value)
            self.selections = selections

    def __init__(self, id_scenario: Optional[Union[int, str]] = None):
        """
        :param id_scenario: the id of scenario. if None, this will be self-increment from 0 to scenarios_number-1
        """
        super().__init__()
        if (id_scenario is not None) and (not isinstance(id_scenario, (int, str))):
            raise MelodieExceptions.Scenario.ScenarioIDTypeError(id_scenario)
        self._parameters = []
        self.manager: Union['Calibrator', 'Simulator', None] = None
        self.id = id_scenario
        self.number_of_run = 1
        self.periods = 0
        self.setup()

    def copy(self) -> 'Scenario':
        new_scenario = self.__class__()
        for property_name, property in self.__dict__.items():
            assert property_name in new_scenario.__dict__
            setattr(new_scenario, property_name, property)
        for parameter in self._parameters:
            parameter.init = getattr(self, parameter.name)
        return new_scenario

    def setup(self):
        pass

    def to_dict(self):
        """

        :return:
        """
        d = {}
        for k in self.__dict__.keys():
            v = self.__dict__[k]
            d[k] = v
        return d

    def properties_as_parameters(self) -> List[BaseParameter]:
        return self._parameters

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.__dict__}>"

    def get_registered_dataframe(self, table_name) -> pd.DataFrame:
        assert self.manager is not None
        return self.manager.get_registered_dataframe(table_name)

    def get_scenarios_table(self) -> pd.DataFrame:
        assert self.manager is not None
        return self.manager.scenarios_dataframe

    def add_interactive_parameters(self, parameters: List[Union[BaseParameter, NumberParameter, SelectionParameter]]):
        self._parameters.extend(parameters)
        temp_set = set()
        for parameter in self._parameters:
            if parameter.name in temp_set:
                raise MelodieExceptions.Scenario.ParameterRedefinedError(parameter.name, self._parameters)
            temp_set.add(parameter.name)
