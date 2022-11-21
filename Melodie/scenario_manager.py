import logging
from typing import List, Optional, Union, TYPE_CHECKING

import numpy as np
import pandas as pd

from MelodieInfra import MelodieExceptions
from .element import Element

if TYPE_CHECKING:
    from Melodie import Calibrator, Simulator
    from .data_loader import DataFrameInfo, MatrixInfo
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
            return (
                f"<class {self.__class__.__name__}, name {self.name}, type {self.type}>"
            )

    class NumberParameter(BaseParameter):
        def __init__(
            self,
            name,
            init_value: Union[int, float],
            min_val: Optional[Union[int, float]] = None,
            max_val: Optional[Union[int, float]] = None,
            step: Optional[Union[int, float]] = None,
        ):
            super().__init__(name, "number", init_value)
            if min_val is None or max_val is None or step is None:
                raise NotImplementedError(
                    "This version of melodie does not support free bound or period yet"
                )
            assert isinstance(init_value, (int, float))
            assert isinstance(max_val, (int, float))
            assert isinstance(min_val, (int, float))
            assert isinstance(step, (int, float))
            self.min = min_val
            self.max = max_val
            self.step = step

    class SelectionParameter(BaseParameter):
        def __init__(
            self,
            name,
            init_value: Union[int, str, bool],
            selections: List[Union[int, str, bool]],
        ):
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
        self.manager: Union["Calibrator", "Simulator", None] = None
        self.id = id_scenario
        self.run_num = 1
        self.period_num = 0

    def copy(self) -> "Scenario":
        """
        Copy self to a new scenario.

        :return:
        """
        new_scenario = self.__class__()
        for property_name, property in self.__dict__.items():
            # assert property_name in new_scenario.__dict__, (property_name, new_scenario.__dict__)
            setattr(new_scenario, property_name, property)
        for parameter in self._parameters:
            parameter.init = getattr(self, parameter.name)
        return new_scenario

    def setup(self):
        """
        Setup method, be sure to inherit it on custom class.

        :return:
        """
        pass

    def to_dict(self):
        """
        Convert to dict

        :return: Dictionary `property_name->property_value`
        """
        d = {}
        for k in self.__dict__.keys():
            v = self.__dict__[k]
            d[k] = v
        return d

    def to_json(self):
        """
        Convert to dict without concerning non-serializable properties.

        :return: Dictionary `property_name->property_value`, without non-serializable properties
        """
        d = {}
        for k in self.__dict__.keys():
            if k not in {"manager"}:
                d[k] = self.__dict__[k]
        return d

    def get_parameters(self) -> List[BaseParameter]:
        """
        Return parameters.

        :return:
        """
        return self._parameters

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.__dict__}>"

    def get_dataframe(self, df_info: "DataFrameInfo") -> pd.DataFrame:
        """
        Get dataframe from scenario

        :param df_info:
        :return: pandas dataframe.
        """
        assert self.manager is not None
        return self.manager.get_dataframe(df_info.df_name)

    def get_matrix(self, matrix_info: "MatrixInfo") -> np.ndarray:
        """
        Get matrix from scenario

        :param matrix_info:
        :return: 2D numpy array
        """
        assert self.manager is not None
        return self.manager.get_matrix(matrix_info.mat_name)

    def add_interactive_parameters(
        self,
        parameters: List[Union[BaseParameter, NumberParameter, SelectionParameter]],
    ):
        """
        For visualizers, interactive parameters makes it possible to tune parameters on frontend.

        :param parameters:
        :return:
        """
        self._parameters.extend(parameters)
        temp_set = set()
        for parameter in self._parameters:
            if parameter.name in temp_set:
                raise MelodieExceptions.Scenario.ParameterRedefinedError(
                    parameter.name, self._parameters
                )
            temp_set.add(parameter.name)
