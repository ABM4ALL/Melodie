import copy
import logging
import os
import pickle
from typing import TYPE_CHECKING, List, Optional, Union

import numpy as np

from MelodieInfra import MelodieExceptions

from .element import Element

if TYPE_CHECKING:
    from Melodie import Calibrator, Simulator

    from .data_loader import DataFrameInfo, MatrixInfo
logger = logging.getLogger(__name__)


class Scenario(Element):
    """
    The Scenario class defines a particular parameterization of the model.

    A Scenario object holds all parameters and data required for a simulation
    run. It is created by the ``Simulator`` or ``Calibrator`` for each scenario
    defined in the input data tables.
    """

    def __init__(self, id_scenario: Optional[Union[int, str]] = 0):
        """
        :param id_scenario: The unique identifier for this scenario. If not
            provided, it will be assigned automatically by the ``Simulator``.
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
        Create a deep copy of the current scenario object.

        :return: A new ``Scenario`` object.
        """
        new_scenario = self.__class__()
        for property_name, property in self.__dict__.items():
            # assert property_name in new_scenario.__dict__, (property_name, new_scenario.__dict__)
            setattr(new_scenario, property_name, property)
        for parameter in self._parameters:
            parameter.init = getattr(self, parameter.name)
        return new_scenario

    def load_data(self):
        """
        A hook for loading static data tables.

        This method is called automatically by the framework after scenario
        parameters have been loaded. It should be used to load any static data
        files (e.g., CSVs, matrices) that the model requires.
        """
        pass

    def setup_data(self):
        """
        A hook for pre-computing data based on scenario parameters.

        This method is called automatically after ``load_data()``. It is useful
        for generating derived data, such as agent parameter DataFrames, before
        the model components are created.
        """
        pass

    def _setup(self, data: dict = None):
        self.setup()
        if data is not None:
            for col_name in data.keys():
                setattr(self, col_name, data[col_name])
        self.load_data()
        self.setup_data()

    def initialize(self):
        """
        A wrapper for the internal ``_setup`` method.

        This should be called if a scenario object is created and set up
        manually, outside the standard ``Simulator`` execution loop.
        """
        self._setup()

    def setup(self):
        """
        A hook for custom scenario initialization.

        This method is called at the beginning of the scenario setup process,
        before parameters are loaded from the scenario table. It can be used
        to define scenario-level properties.
        """
        pass

    def load_dataframe(self, df_info: Union[str, "DataFrameInfo"]):
        """
        Load a data frame from a table file in the input directory.

        :param df_info: The name of the CSV or Excel file (e.g.,
            ``'my_data.csv'``).
        """

        assert self.manager is not None, MelodieExceptions.MLD_INTL_EXC
        assert self.manager.data_loader is not None, MelodieExceptions.MLD_INTL_EXC
        return self.manager.data_loader.load_dataframe(df_info)

    def load_matrix(self, mat_info: Union[str, "MatrixInfo"]) -> np.ndarray:
        """
        Load a matrix from a table file in the input directory.

        :param mat_info: The name of the CSV or Excel file (e.g.,
            ``'my_matrix.csv'``).
        """

        assert self.manager is not None, MelodieExceptions.MLD_INTL_EXC
        assert self.manager.data_loader is not None, MelodieExceptions.MLD_INTL_EXC
        return self.manager.data_loader.load_matrix(mat_info)

    def to_dict(self):
        """
        Convert this scenario object to a dictionary.

        :return: A ``dict`` mapping property names to their values.
        """
        d = {}
        for k in self.__dict__.keys():
            v = self.__dict__[k]
            d[k] = v
        return d

    def to_json(self):
        """
        Convert the scenario to a JSON-serializable dictionary.

        This method excludes properties that cannot be serialized, such as the
        'manager' object, pandas DataFrames, and numpy arrays. These excluded
        objects will be reloaded independently in worker processes via the
        ``load_data()`` method.

        :return: A ``dict`` containing serializable properties.
        """
        import pandas as pd
        import numpy as np

        d = {}
        for k in self.__dict__.keys():
            if k.startswith("_"):
                continue
            v = self.__dict__[k]
            # Skip non-serializable objects
            if k == "manager":
                continue
            if isinstance(v, (pd.DataFrame, np.ndarray)):
                continue
            d[k] = v
        return d

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.__dict__}>"

    def get_dataframe(self, df_info: "DataFrameInfo") -> "pd.DataFrame":
        """
        (Internal) Get a dataframe from the scenario.

        :param df_info: A ``DataFrameInfo`` object.
        :return: A pandas DataFrame.
        """
        assert self.manager is not None
        return self.manager.get_dataframe(df_info.df_name)

    def get_matrix(self, matrix_info: "MatrixInfo") -> "np.ndarray":
        """
        (Internal) Get a matrix from the scenario.

        :param matrix_info: A ``MatrixInfo`` object.
        :return: A 2D numpy array.
        """
        assert self.manager is not None
        return self.manager.get_matrix(matrix_info.mat_name)
