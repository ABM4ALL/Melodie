import os
from typing import Optional, Dict, List, Union, Callable, Type

import numpy as np
import pandas as pd
import sqlalchemy

from MelodieInfra import DBConn, create_db_conn, MelodieExceptions, Config

from .scenario_manager import Scenario
from .table_generator import DataFrameGenerator

class DataFrameInfo:
    """
    DataFrameInfo provides standard format for input tables as parameters.
    """
    df_name: str
    columns: Dict[str, "sqlalchemy.types"]
    file_name: Optional[str] = None

    def __init__(
            self,
            df_name: str,
            columns: Dict[str, "sqlalchemy.types"],
            file_name: Optional[str] = None,
    ):
        """
        :param df_name: Name of dataframe.
        :param columns: A dict, ``column name --> column data type``.
        :param file_name: File name to load this dataframe, None by default. If None, be sure to
            generate the dataframe in the DataLoader.
        """
        self.df_name: str = df_name
        self.columns: Dict[str, "sqlalchemy.types"] = columns
        self.file_name: Optional[str] = file_name

    def check_column_names(self, columns: List[str]):
        if set(columns) != set(self.columns.keys()):
            missing = set(self.columns.keys()).difference(set(columns))
            undefined = set(set(columns)).difference(self.columns.keys())
            raise MelodieExceptions.Data.ColumnNameConsistencyError(
                self.df_name, missing, undefined
            )


class MatrixInfo:
    """
    MatrixInfo provides standard format for input matrices as parameters.
    """
    def __init__(
            self,
            mat_name: str,
            data_type: "sqlalchemy.types",
            file_name: Optional[str] = None,
    ):
        """
        :param mat_name: Name of the current matrix.
        :param columns: A type indicating the data type in the matrix.
        :param file_name: File name to load this dataframe, None by default. If None, be sure to
            generate the dataframe in the DataLoader.
        """
        self.mat_name: str = mat_name
        self.data_type: sqlalchemy.types = data_type
        self.file_name: Optional[str] = file_name

    @property
    def dtype(self):
        py_type = self.data_type.python_type
        if issubclass(py_type, int):
            return np.int64
        elif issubclass(py_type, float):
            return np.float64
        else:
            raise NotImplementedError(
                f"Cannot convert this type {self.data_type} to numpy data type!"
            )


class DataLoader:
    """
    DataLoader loads dataframes or matrices.
    
    ``Simulator``/``Trainer``/``Calibrator`` will have reference to DataLoader to avoid defining tables multiple times.
    """

    def __init__(
            self,
            manager,
            config: Config,
            scenario_cls: Type[Scenario],
            as_sub_worker=False,
    ):
        """
        :param manager: The ``Simulator``/``Trainer``/``Calibrator`` this dataloader belongs to.
        :param config: A ``Melodie.Config`` instance, the configuration in current project.
        :param scenario_cls: The class of scenario used in this project.
        :param as_sub_worker: If True, DataLoader will be disabled to avoid unneed database operations.
        """
        MelodieExceptions.Assertions.NotNone(
            scenario_cls, "Scenario class should not be None!"
        )
        self.as_sub_worker = as_sub_worker  # If loader is loaded from sub worker.
        self.config: Config = config
        self.scenario_cls = scenario_cls
        self.registered_dataframes: Optional[Dict[str, pd.DataFrame]] = {}
        self.registered_matrices: Optional[Dict[str, np.ndarray]] = {}
        self.manager = manager
        self.manager.data_loader = self
        self.setup()

    def setup(self):
        pass

    def register_dataframe(
            self, table_name: str, data_frame: pd.DataFrame, data_types: dict = None
    ) -> None:
        """
        Register a pandas dataframe.

        :param table_name: Name of dataframe
        :param data_frame: A pandas dataframe
        :param data_types: A dictionary describing data types.
        :return: None
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

    def load_dataframe(self, df_info: "DataFrameInfo") -> None:
        """
        Register static table. The static table will be copied into database.

        The scenarios/agents parameter tables can also be registered by this method.

        :return: None
        """
        table_name = df_info.df_name
        file_name = df_info.file_name
        data_types = df_info.columns
        _, ext = os.path.splitext(file_name)
        table: Optional[pd.DataFrame]

        MelodieExceptions.Data.TableNameInvalid(table_name)
        if ext in {".xls", ".xlsx"}:
            file_path_abs = os.path.join(self.config.input_folder, file_name)
            table = pd.read_excel(file_path_abs)
            df_info.check_column_names(list(table.columns))
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

        self.registered_dataframes[table_name] = create_db_conn(
            self.config
        ).read_dataframe(table_name)

    def load_matrix(self, matrix_info: "MatrixInfo") -> None:
        """
        Register static matrix.

        :return: None
        """
        _, ext = os.path.splitext(matrix_info.file_name)
        if ext in {".xls", ".xlsx"}:
            file_path_abs = os.path.join(
                self.config.input_folder, matrix_info.file_name
            )
            table: pd.DataFrame = pd.read_excel(file_path_abs, header=None)
            array = table.to_numpy(matrix_info.dtype, copy=True)
        else:
            raise NotImplementedError(f"Cannot load file to matrix {ext}")
        self.registered_matrices[matrix_info.mat_name] = array

    def dataframe_generator(
            self,
            df_info: DataFrameInfo,
            rows_in_scenario: Union[int, Callable[[Scenario], int]],
    ) -> DataFrameGenerator:
        """
        Create a new generator for dataframes.

        :param df_info: Dataframe info indicating the dataframe to be generated.
        :param rows_in_scenario: How many rows will be generated for a specific scenario. \
            This argument should be an integer as number of rows for each scenario, or a function with a parameter \
            with type `Scenario` and return an integer for how many rows to generate for this scenario .
        :return: A dataframe generator object
        """
        return DataFrameGenerator(self, df_info, rows_in_scenario)

    def generate_scenarios_from_dataframe(self, df_name: str) -> List["Scenario"]:
        """
        Generate scenario objects by the parameter from static table named ``df_name``.

        :param df_name: Name of static table.
        :return: A list of scenario object.
        """
        scenarios_dataframe = self.registered_dataframes.get(df_name)
        if scenarios_dataframe is None:
            MelodieExceptions.Data.TableNotFound(df_name, self.registered_dataframes)

        cols = [col for col in scenarios_dataframe.columns]
        scenarios: List[Scenario] = []
        for i in range(scenarios_dataframe.shape[0]):
            scenario = self.scenario_cls()
            scenario.manager = self.manager
            scenario.setup()

            for col_name in cols:
                value = scenarios_dataframe.loc[i, col_name]
                if isinstance(value, str):
                    scenario.__dict__[col_name] = value
                else:
                    scenario.__dict__[col_name] = value.item()
            scenarios.append(scenario)
        if len(scenarios) == 0:
            raise MelodieExceptions.Scenario.NoValidScenarioGenerated(scenarios)
        return scenarios

    def generate_scenarios(self, manager_type: str) -> List["Scenario"]:
        """
        Generate scenario objects by the parameter from static tables or scenarios_dataframe.

        :param manager_type: The type of scenario manager, a ``str`` in "simulator", "trainer" or "calibrator".
        :return: A list of scenarios.
        """
        if manager_type not in {"simulator", "trainer", "calibrator"}:
            MelodieExceptions.Program.Variable.VariableNotInSet(
                "manager_type", manager_type, {"simulator", "trainer", "calibrator"}
            )
        return self.generate_scenarios_from_dataframe(f"{manager_type}_scenarios")
