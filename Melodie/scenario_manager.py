import os
import logging
from typing import List, Optional, Union, ClassVar, TYPE_CHECKING, Dict, Tuple

import numpy
import numpy as np

from Melodie.element import Element
from Melodie.db import DB, create_db_conn
from .basic.exceptions import MelodieExceptions
import pandas as pd

from .basic.fileio import load_excel, batch_load_tables, load_all_excel_file
from .config import Config

if TYPE_CHECKING:
    from Melodie import Calibrator, Simulator
logger = logging.getLogger(__name__)


class Scenario(Element):
    class BaseParameter():
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
            self.min = min_val
            self.max = max_val
            self.step = step

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
        self.manager: Union['Calibrator', 'Simulator', None] = None
        self.id = id_scenario
        self.number_of_run = 1
        self.periods = 0
        self.setup()

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
            # if np.isscalar(v):
            #     d[k] = v
            # else:
            #     logger.warning("type(self.__dict__[k]) is not a scal")
        return d

    def properties_as_parameters(self) -> List[BaseParameter]:
        return []

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.__dict__}>"

    def get_registered_dataframe(self, table_name) -> pd.DataFrame:
        assert self.manager is not None
        return self.manager.get_registered_dataframe(table_name)

    def get_scenarios_table(self) -> pd.DataFrame:
        assert self.manager is not None
        return self.manager.scenarios_dataframe


class LearningScenario(Scenario):
    """
    Learning scenario is used in Trainer and Calibrator for trainer/calibrator parameters.
    """

    class Parameter():
        def __init__(self, name: str, min: float, max: float):
            self.name = name
            self.min = min
            self.max = max

        def __repr__(self):
            return f"<{self.__class__.__name__} '{self.name}', range ({self.min}, {self.max})>"

    def __init__(self, id: int, number_of_path: int):
        self.id: int = id
        self.number_of_path: int = number_of_path
        self.parameters: List[LearningScenario.Parameter] = []

    def get_agents_parameters_range(self, agent_num) -> List[Tuple[float, float]]:
        parameters = []
        for agent_id in range(agent_num):
            parameters.extend([(parameter.min, parameter.max) for parameter in self.parameters])
        return parameters


class GATrainerScenario(LearningScenario):
    def __init__(self, id: int, number_of_path: int, number_of_generation: int, strategy_population: int,
                 mutation_prob: int, strategy_param_code_length: int):
        super().__init__(id, number_of_path)
        self.number_of_generation = number_of_generation
        self.strategy_population = strategy_population
        self.mutation_prob = mutation_prob
        self.strategy_param_code_length = strategy_param_code_length

    @staticmethod
    def from_dataframe_record(record: Dict[str, Union[int, float]]) -> 'GATrainerScenario':
        s = GATrainerScenario(record['id'], record['number_of_path'], record['number_of_generation'],
                              record['strategy_population'], record['mutation_prob'],
                              record['strategy_param_code_length'])
        max_values = {name[:len(name) - len("_max")]: value for name, value in record.items() if name.endswith("_max")}
        min_values = {name[:len(name) - len("_min")]: value for name, value in record.items() if name.endswith("_min")}
        print(max_values, min_values)
        assert len(max_values) == len(min_values)
        for k in max_values.keys():
            s.parameters.append(LearningScenario.Parameter(k, min_values[k], max_values[k]))
        return s


class GACalibrationScenario(LearningScenario):
    def __init__(self, id: int, number_of_path: int, generation: int, strategy_population: int,
                 mutation_prob: int, strategy_param_code_length: int):
        super().__init__(id, number_of_path)
        self.calibration_generation = generation
        self.strategy_population = strategy_population
        self.mutation_prob = mutation_prob
        self.strategy_param_code_length = strategy_param_code_length

    @staticmethod
    def from_dataframe_record(record: Dict[str, Union[int, float]]) -> 'GACalibrationScenario':
        s = GACalibrationScenario(record['id'], record['number_of_path'], record['calibration_generation'],
                                  record['strategy_population'], record['mutation_prob'],
                                  record['strategy_param_code_length'])
        max_values = {name[:len(name) - len("_max")]: value for name, value in record.items() if name.endswith("_max")}
        min_values = {name[:len(name) - len("_min")]: value for name, value in record.items() if name.endswith("_min")}
        print(max_values, min_values)
        assert len(max_values) == len(min_values)
        for k in max_values.keys():
            s.parameters.append(LearningScenario.Parameter(k, min_values[k], max_values[k]))
        return s
