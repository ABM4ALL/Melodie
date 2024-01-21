import copy
import logging
import os
import pickle
from typing import List, Optional, Union, TYPE_CHECKING

import numpy as np

from MelodieInfra import MelodieExceptions
from .element import Element

if TYPE_CHECKING:
    from Melodie import Calibrator, Simulator
    from .data_loader import DataFrameInfo, MatrixInfo
logger = logging.getLogger(__name__)


class Scenario(Element):
    """
    Scenario contains a set of parameters used in simulation model.
    It is created before the initialization of ``Model``.

    """

    def __init__(self, id_scenario: Optional[Union[int, str]] = 0):
        """
        :param id_scenario: the id of scenario. if None, this will be self-increment from 0 to scenarios_number-1
        """
        super().__init__()
        if (id_scenario is not None) and (not isinstance(id_scenario, (int, str))):
            raise MelodieExceptions.Scenario.ScenarioIDTypeError(id_scenario)
        self._parameters = []
        self.manager: Union["Calibrator", "Simulator", None] = None
        self.id = id_scenario
        self.id_run = -1
        self.run_num = 1
        self.period_num = 0

    def copy(self) -> "Scenario":
        """
        Copy current scenario to a new scenario.

        :return: New scenario object.
        """
        new_scenario = self.__class__()
        for property_name, property in self.__dict__.items():
            # assert property_name in new_scenario.__dict__, (property_name, new_scenario.__dict__)
            setattr(new_scenario, property_name, property)
        for parameter in self._parameters:
            parameter.init = getattr(self, parameter.name)
        return new_scenario

    def load(self):
        """
        This method loads should load data into the scenario as its properties.
        """
        pass

    def _setup(self):
        self.load()
        self.setup()
    
    def initialize(self):
        """
        Have same effect as calling `_setup`, and must be called when generating scenarios.
        """
        self._setup()

    def setup(self):
        """
        Setup method, be sure to inherit it on the custom scenario class.
        """
        pass

    def load_dataframe(self, df_info: Union[str, "DataFrameInfo"]):
        """
        Load a data frame from table file.

        :df_info: The file name of that containing the data frame, or pass a `DataFrameInfo`
        """

        assert self.manager is not None, MelodieExceptions.MLD_INTL_EXC
        assert self.manager.data_loader is not None, MelodieExceptions.MLD_INTL_EXC
        return self.manager.data_loader.load_dataframe(df_info)

    def load_matrix(self, mat_info: Union[str, "MatrixInfo"]) -> np.ndarray:
        """
        Load a matrix from table file.

        :mat_info: The file name of that containing the matrix, or pass a `DataFrameInfo`
        """

        assert self.manager is not None, MelodieExceptions.MLD_INTL_EXC
        assert self.manager.data_loader is not None, MelodieExceptions.MLD_INTL_EXC
        return self.manager.data_loader.load_matrix(mat_info)

    def to_dict(self):
        """
        Convert this scenario object to a dict.

        :return: A ``dict``, ``property_name->property_value``
        """
        d = {}
        for k in self.__dict__.keys():
            v = self.__dict__[k]
            d[k] = v
        return d

    def to_json(self):
        """
        Convert this scenario to a dict without concerning non-serializable properties.

        :return: a ``dict``, ``property_name->property_value``, without non-serializable properties
        """
        d = {}
        for k in self.__dict__.keys():
            if k not in {"manager"}:
                d[k] = self.__dict__[k]
        return d

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.__dict__}>"

    def get_dataframe(self, df_info: "DataFrameInfo") -> "pd.DataFrame":
        """
        Get dataframe from scenario

        :param df_info:
        :return: pandas dataframe.
        """
        assert self.manager is not None
        return self.manager.get_dataframe(df_info.df_name)

    def get_matrix(self, matrix_info: "MatrixInfo") -> "np.ndarray":
        """
        Get matrix from scenario.

        :param matrix_info:
        :return: 2D numpy array
        """
        assert self.manager is not None
        return self.manager.get_matrix(matrix_info.mat_name)
