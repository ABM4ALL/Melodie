import os
from typing import List, Optional, Union, ClassVar

from Melodie.element import Element
from Melodie.db import DB, create_db_conn
from .basic.exceptions import MelodieExceptions
import pandas as pd

from .basic.fileio import load_excel, batch_load_tables
from .config import Config


class Scenario(Element):
    def __init__(self, id_scenario: Optional[Union[int, str]] = None, agent_num=0):
        """

        :param id_scenario: the id of scenario. if None, this will be self-increment from 0 to scenarios_number-1
        """
        super().__init__()
        if (id_scenario is not None) and (not isinstance(id_scenario, (int, str))):
            raise MelodieExceptions.Scenario.ScenarioIDTypeError(id_scenario)
        self.id = id_scenario
        self.agent_num = agent_num
        self.number_of_run = 1
        self.setup()
        assert self.agent_num > 0

    def setup(self):
        pass

    def toDict(self):
        d = {}
        for k in self.params:
            d[k] = self.__dict__[k]
        return d

    def __repr__(self):
        return str(self.__dict__)


class ScenarioManager:
    def __init__(self, config: Config, scenario_class: ClassVar['Scenario'] = None):
        # TODO : Load scenario from excel/csv/database.
        # TODO: 模型启动尽量只用scenarios一张表。也就是
        # TODO: 最好改成直接读excel表，将其变成dataframe.
        # TODO: 有的模型可能需要几张scenario表。现在的表还不够！有的表中，每个Agent的参数都要提前设置好。
        # TODO: scenario表的有一些参数，可能指向另一张表

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
            self.xls_path = config.parameters_xls_file
            assert os.path.exists(self.xls_path)
            scenarios, agent_params = load_excel(self.xls_path)
            self.save(scenarios, agent_params)
            tables = batch_load_tables(config.static_xls_files, DB.RESERVED_TABLES)
            for table_name, table in tables.items():
                create_db_conn().write_dataframe(table_name, table, 'replace')
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
        create_db_conn().write_dataframe(DB.SCENARIO_TABLE, self.to_dataframe(), 'replace')

    def save(self, scenario_df: pd.DataFrame, agent_param_df: pd.DataFrame):
        create_db_conn().write_dataframe(DB.SCENARIO_TABLE, scenario_df, 'replace')
        create_db_conn().write_dataframe(DB.AGENT_PARAM_TABLE, agent_param_df, 'replace')

    def load_scenarios(self) -> List[Scenario]:
        table = create_db_conn().read_dataframe(DB.SCENARIO_TABLE)
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
