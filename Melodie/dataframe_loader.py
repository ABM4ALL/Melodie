import abc
import os
from typing import Optional, Dict, List, ClassVar, Union, Callable

import pandas as pd

from Melodie import TableGenerator, Scenario
from Melodie.config import Config

from Melodie.db import DB, create_db_conn


class DataFrameLoader:
    """
    TableLoader loads tables
    Simulator/Trainer/Calibrator will have reference to TableLoader for loading tables without defining tables multiple times.
    """

    def __init__(self, manager, config: Config, scenario_class: ClassVar[Scenario]):
        self.config: Config = config
        self.scenario_class = scenario_class
        self.registered_dataframes: Optional[Dict[str, pd.DataFrame]] = {}
        self.manager = manager

    @abc.abstractmethod
    def register_scenario_dataframe(self) -> None:
        """
        This method must be overriden.
        The "scenarios" table will be registered in this method.
        """
        pass

    def register_static_dataframes(self) -> None:
        """
        The "agent_params" table can be registered in this method.
        """
        pass

    def register_generated_dataframes(self) -> None:
        """
        The "agent_params" table can be registered in this method.
        """
        pass

    def register_dataframe(self, table_name: str, data_frame: pd.DataFrame, data_types: dict = None) -> None:
        """

        :param table_name:
        :param data_frame:
        :param data_types:
        :return:
        """
        if data_types is None:
            data_types = {}
        DB.register_dtypes(table_name, data_types)
        create_db_conn(self.config).write_dataframe(table_name, data_frame, data_types=data_types,
                                                    if_exists="replace")
        self.registered_dataframes[table_name] = create_db_conn(self.config).read_dataframe(table_name)

    def load_dataframe(self, table_name: str, file_name: str, data_types: dict) -> None:

        """
        Register static table, saving it to `self.registered_dataframes`.
        The static table will be copied into database.

        If the scenarios/agents parameter tables can also be registered by this method.

        :param table_name: The table name, and same the name of table in database.
        :param file_name: The excel filename.
            if ends with `.xls` or `.xlsx`, This file will be searched at Config.excel_folder
        :param data_types: Type information in a dict
        :return:
        """
        _, ext = os.path.splitext(file_name)
        table: Optional[pd.DataFrame]
        assert table_name.isidentifier(), f"table_name `{table_name}` was not an identifier!"
        if ext in {'.xls', '.xlsx'}:
            file_path_abs = os.path.join(self.config.excel_source_folder, file_name)
            table = pd.read_excel(file_path_abs)
        else:
            raise NotImplemented(file_name)

        DB.register_dtypes(table_name, data_types)
        create_db_conn(self.config).write_dataframe(table_name, table, data_types=data_types,
                                                    if_exists="replace", )

        self.registered_dataframes[table_name] = create_db_conn(self.config).read_dataframe(table_name)

    def new_table_generator(self, table_name: str, rows_in_scenario: Union[int, Callable[[Scenario], int]]):
        """
        Create a new generator
        :param table_name:
        :param rows_in_scenario:
            How many rows will be generated for a specific scenario.
            This argument should be an integer as number of rows for each scenario, or a function with a parameter typed
            `Scenario` and return an integer for how many rows to generate for this scenario .
        :return:
        """
        return TableGenerator(self, table_name, rows_in_scenario)

    def generate_scenarios_from_dataframe(self, df_name: str) -> List['Scenario']:
        """
        Generate scenario objects by the parameter from static tables
        :return:
        """
        scenarios_dataframe = self.registered_dataframes[df_name]
        assert scenarios_dataframe is not None
        assert self.scenario_class is not None

        cols = [col for col in scenarios_dataframe.columns]
        scenarios: List[Scenario] = []
        for i in range(scenarios_dataframe.shape[0]):
            scenario = self.scenario_class()
            scenario.manager = self.manager
            for col_name in cols:
                assert col_name in scenario.__dict__.keys(), f"col_name: '{col_name}', scenario: {scenario}"
                scenario.__dict__[col_name] = scenarios_dataframe.loc[i, col_name]
            scenarios.append(scenario)
        assert len(scenarios) != 0
        return scenarios

    def generate_scenarios(self) -> List['Scenario']:
        """
        Generate scenario objects by the parameter from static tables or scenarios_dataframe.
        :return:
        """
        return self.generate_scenarios_from_dataframe('scenarios')