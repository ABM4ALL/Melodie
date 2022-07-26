import abc
import sqlalchemy
import os
from typing import Optional, Dict, List, ClassVar, Union, Callable
from dataclasses import dataclass
import pandas as pd

from Melodie import TableGenerator, Scenario
from Melodie.basic import MelodieExceptions
from Melodie.config import Config

from Melodie.db import DBConn, create_db_conn


@dataclass
class DataFrameInfo:
    df_name: str
    file_name: str
    columns: Dict[str, 'sqlalchemy.types']

    @property
    def data_types(self) -> dict:
        dtypes = {}
        for key, value in self.columns.items():
            dtypes[key] = value
        return dtypes


class DataFrameLoader:
    """
    TableLoader loads tables
    Simulator/Trainer/Calibrator will have reference to TableLoader for loading tables without defining tables multiple times.
    """

    def __init__(self, manager, config: Config, scenario_cls: ClassVar[Scenario]):
        MelodieExceptions.Assertions.NotNone(
            scenario_cls, "Scenario class should not be None!"
        )
        self.as_sub_worker = False  # If loader is loaded from sub worker.
        self.config: Config = config
        self.scenario_cls = scenario_cls
        self.registered_dataframes: Optional[Dict[str, pd.DataFrame]] = {}
        self.manager = manager
        self.setup()

    def setup(self):
        pass

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

    def register_dataframe(
        self, table_name: str, data_frame: pd.DataFrame, data_types: dict = None
    ) -> None:
        """
        :param table_name:
        :param data_frame:
        :param data_types:
        :return:
        """
        if data_types is None:
            data_types = {}
        if not self.as_sub_worker:
            DBConn.register_dtypes(table_name, data_types)
            create_db_conn(self.config).write_dataframe(
                table_name, data_frame, data_types=data_types, if_exists="replace"
            )
        self.registered_dataframes[table_name] = create_db_conn(
            self.config
        ).read_dataframe(table_name)

    def load_dataframe(self, df_info: 'DataFrameInfo') -> None:

        """
        Register static table, saving it to `self.registered_dataframes`.
        The static table will be copied into database.

        If the scenarios/agents parameter tables can also be registered by this method.

        :param table_name: The table name, and same the name of table in database. Table name should be an identifier.
        :param file_name: The excel filename.
            if ends with `.xls` or `.xlsx`, This file will be searched at Config.excel_folder
        :param data_types: Type information in a dict
        :return:
        """
        table_name = df_info.df_name
        file_name = df_info.file_name
        data_types = df_info.data_types
        _, ext = os.path.splitext(file_name)
        table: Optional[pd.DataFrame]

        MelodieExceptions.Data.TableNameInvalid(table_name)
        if ext in {".xls", ".xlsx"}:
            file_path_abs = os.path.join(self.config.excel_source_folder, file_name)
            table = pd.read_excel(file_path_abs)
        else:
            raise NotImplemented(file_name)
        if not self.as_sub_worker:
            DBConn.register_dtypes(table_name, data_types)
            create_db_conn(self.config).write_dataframe(
                table_name,
                table,
                data_types=data_types,
                if_exists="replace",
            )

        self.registered_dataframes[table_name] = create_db_conn(self.config).read_dataframe(table_name)

    def table_generator(
        self, table_name: str, rows_in_scenario: Union[int, Callable[[Scenario], int]]
    ):
        """
        Create a new generator
        :param table_name:
        :param rows_in_scenario: How many rows will be generated for a specific scenario. \
            This argument should be an integer as number of rows for each scenario, or a function with a parameter \
            with type `Scenario` and return an integer for how many rows to generate for this scenario .
        :return:
        """
        return TableGenerator(self, table_name, rows_in_scenario)

    def generate_scenarios_from_dataframe(self, df_name: str) -> List["Scenario"]:
        """
        Generate scenario objects by the parameter from static tables
        :return:
        """
        scenarios_dataframe = self.registered_dataframes.get(df_name)
        if scenarios_dataframe is None:
            MelodieExceptions.Data.TableNotFound(df_name, self.registered_dataframes)

        cols = [col for col in scenarios_dataframe.columns]
        scenarios: List[Scenario] = []
        for i in range(scenarios_dataframe.shape[0]):
            scenario = self.scenario_cls()
            scenario.manager = self.manager
            for col_name in cols:
                if col_name not in scenario.__dict__.keys():
                    raise MelodieExceptions.Data.TableColumnDoesNotMatchObjectProperty(
                        df_name, col_name, scenario
                    )
                value = scenarios_dataframe.loc[i, col_name]
                if isinstance(value, str):
                    scenario.__dict__[col_name] = value
                else:
                    scenario.__dict__[col_name] = value.item()
            scenarios.append(scenario)
        if len(scenarios) == 0:
            raise MelodieExceptions.Scenario.ScenariosIsEmptyList()
        return scenarios

    def generate_scenarios(self, manager_type: str) -> List["Scenario"]:
        """
        Generate scenario objects by the parameter from static tables or scenarios_dataframe.
        :return:
        """
        if manager_type not in {"simulator", "trainer", "calibrator"}:
            MelodieExceptions.Program.Variable.VariableNotInSet(
                "manager_type", manager_type, {"simulator", "trainer", "calibrator"}
            )
        return self.generate_scenarios_from_dataframe(f"{manager_type}_scenarios")
