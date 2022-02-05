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
    def __init__(self, id: int, number_of_path: int, training_generation: int, strategy_population: int,
                 mutation_prob: int, strategy_param_code_length: int):
        super().__init__(id, number_of_path)
        self.training_generation = training_generation
        self.strategy_population = strategy_population
        self.mutation_prob = mutation_prob
        self.strategy_param_code_length = strategy_param_code_length

    @staticmethod
    def from_dataframe_record(record: Dict[str, Union[int, float]]) -> 'GATrainerScenario':
        s = GATrainerScenario(record['id'], record['number_of_path'], record['training_generation'],
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


class ScenarioManager:
    def __init__(self, config: Config, scenario_class: ClassVar['Scenario'] = None):
        self.config = config
        self.param_source = config.parameters_source
        self.scenario_class = scenario_class

        if self.param_source == 'generate':
            self._scenarios = self.gen_scenarios()
            if not isinstance(self._scenarios, list):
                raise MelodieExceptions.Scenario.NoValidScenarioGenerated(self._scenarios)
            elif len(self._scenarios) == 0:
                raise MelodieExceptions.Scenario.ScenariosIsEmptyList()
            self.scenario_class = self._scenarios[0].__class__
            self.check_scenarios()
            self.save_scenarios()

        elif self.param_source == 'from_file':
            self.xls_folder = config.excel_source_folder
            assert os.path.exists(self.xls_folder)
            scenarios, agent_params, tables = load_all_excel_file(
                [os.path.join(self.xls_folder, file) for file in os.listdir(self.xls_folder)],
                DB.RESERVED_TABLES)
            # scenarios, agent_params = load_excel(self.xls_path)
            self.save(scenarios, agent_params)
            # tables = batch_load_tables(config.static_xls_files, DB.RESERVED_TABLES)
            for table_name, table in tables.items():
                create_db_conn(self.config).write_dataframe(table_name, table, 'replace')

        elif self.param_source == 'from_database':
            raise NotImplementedError
        else:
            raise NotImplementedError

    def check_scenarios(self):
        """
        Auto insert self-increment scenario id into all scenarios if all scenario.id are None,
        and check scenarios ids to make sure scenario id are not duplicated.

        The Scenario.id can only be of two cases:
        1. All of type `int` or All of type `string`, such as [1, 2, 3, 4, 5] or [1, 3, 5, 7, 9] or ['a', 'b', 'c']
        2. All of None
        The following cases are not allowed:
        1. Mixing int and string into the ids, such as [1, 2, 'a', 'b']
        2. Mixing None and not-None values, such as [1, 2, None]
        3. Using float, tuple or Mutable objects for id value, such as [123.456, 234.567].

        :return:
        """
        count_nones = 0
        scenario_id_type = ''
        for scenario in self._scenarios:
            if not isinstance(scenario, Scenario):
                raise MelodieExceptions.Scenario.ScenarioListItemTypeError(scenario)
            if scenario.id is None:
                count_nones += 1
            elif not isinstance(scenario.id, (int, str)):
                raise MelodieExceptions.Scenario.ScenarioIDTypeError(scenario.id)
            else:
                try:
                    if isinstance(scenario.id, str):
                        assert scenario_id_type == '' or scenario_id_type == 'str'
                        scenario_id_type = 'str'
                    else:
                        assert scenario_id_type == '' or scenario_id_type == 'int'
                        scenario_id_type = 'int'

                except AssertionError:
                    raise MelodieExceptions.Scenario.ScenarioIDNotOfSameTypeError(scenario.id, scenario_id_type)
        if count_nones > 0:
            if count_nones == len(self._scenarios):
                scenario_id = 0
                for scenario in self._scenarios:
                    scenario.id = scenario_id
                    scenario_id += 1
            else:
                raise MelodieExceptions.Scenario.ScenarioIDNotAllNoneError(count_nones, len(self._scenarios))

        id_set = set()
        for scenario in self._scenarios:
            if scenario.id in id_set:
                raise MelodieExceptions.Scenario.ScenarioIDDuplicatedError(scenario.id)
            id_set.add(scenario.id)

    def gen_scenarios(self) -> List[Scenario]:
        """
        The method to generate scenarios.
        :return:
        """
        pass

    def to_dataframe(self) -> pd.DataFrame:
        """
        :return:
        """
        data_list = []
        for scenario in self._scenarios:
            data_list.append(scenario.__dict__)
        df = pd.DataFrame(data_list)
        return df

    def save_scenarios(self):
        if self.config.with_db:
            create_db_conn(self.config).write_dataframe(DB.SCENARIO_TABLE, self.to_dataframe(), 'replace')
        else:
            logger.warning('Config.with_db was False, scenarios will not be created and nothing will be saved.')

    def save(self, scenario_df: pd.DataFrame, agent_param_df: pd.DataFrame):
        if self.config.with_db:
            create_db_conn(self.config).write_dataframe(DB.SCENARIO_TABLE, scenario_df, 'replace')
            create_db_conn(self.config).write_dataframe(DB.AGENT_PARAM_TABLE, agent_param_df, 'replace')
        else:
            logger.warning('Config.with_db was False, scenarios and agent parameters will not be saved.')

    def load_scenarios(self) -> List[Scenario]:
        table = create_db_conn(self.config).read_dataframe(DB.SCENARIO_TABLE)
        cols = [col for col in table.columns]
        scenarios: List[Scenario] = []
        for i in range(table.shape[0]):
            scenario = self.scenario_class()
            for col_name in cols:
                assert col_name in scenario.__dict__.keys()
                scenario.__dict__[col_name] = table.loc[i, col_name]
            scenarios.append(scenario)
        assert len(scenarios) != 0
        return scenarios
