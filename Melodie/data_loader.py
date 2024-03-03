import hashlib
import logging
import os
import shutil
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Type, Union

import cloudpickle
import numpy as np
import pandas
import pandas as pd
import sqlalchemy

from MelodieInfra import Config, DBConn, MelodieExceptions, Table, TableInterface
from MelodieInfra.table.table_general import GeneralTable
from MelodieInfra.utils import PickledCacheFileReader, underline_to_camel

from .scenario_manager import Scenario
from .table_generator import DataFrameGenerator

logger = logging.getLogger(__name__)


class DataFrameInfo:
    """
    DataFrameInfo provides standard format for input tables as parameters.
    """

    df_name: str
    columns: Dict[str, "sqlalchemy.types"]
    file_name: Optional[str] = None
    engine: str

    FORCE_PANDAS = False  # Force Melodie to use Pandas to load all dataframes.

    def __init__(
        self,
        df_name: str,
        columns: Dict[str, "sqlalchemy.types"],
        file_name: str = "",
        engine: str = "pandas",
    ):
        """
        :param df_name: Name of dataframe.
        :param columns: A dict, ``column name --> column data type``.
        :param file_name: File name to load this dataframe, None by default. If None, be sure to
            generate the dataframe in the DataLoader.
        :param engine: The library used to load this table file. Valid values are "pandas" and "melodie-table".
            However, if ``DataFrameInfo.FORCE_PANDAS`` was ``True``, Melodie will use ``"pandas"`` to load all dataframes.
        """
        self.df_name: str = df_name
        self.columns: Dict[str, "sqlalchemy.types"] = columns
        self.file_name: str = file_name
        assert engine in {"pandas", "melodie-table"}
        self.engine = engine if not DataFrameInfo.FORCE_PANDAS else "pandas"

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
        data_type: Optional["sqlalchemy.types"] = None,
        file_name: Optional[str] = None,
    ):
        """
        :param mat_name: Name of the current matrix.
        :param columns: A type indicating the data type in the matrix.
        :param file_name: File name to load this dataframe, None by default. If None, be sure to
            generate the dataframe in the DataLoader.
        """
        self.mat_name: str = mat_name
        self.data_type: "sqlalchemy.types" = data_type
        self.file_name: Optional[str] = file_name

    @property
    def dtype(self):
        if self.data_type is None:
            return None
        py_type = self.data_type.python_type
        if issubclass(py_type, int):
            return np.int64
        elif issubclass(py_type, float):
            return np.float64
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
        # If loader is loaded from sub worker.
        self.as_sub_worker = as_sub_worker
        self.config: Config = config
        self.scenario_cls = scenario_cls
        self.registered_dataframes: Dict[str, "pd.DataFrame"] = {}
        self.registered_matrices: Dict[str, "np.ndarray"] = {}
        self.manager = manager
        self.manager.data_loader = self
        self.load_scenarios()
        self.setup()

    def load_scenarios(self):
        for file_name in os.listdir(self.config.input_folder):
            camel_case = underline_to_camel(os.path.splitext(file_name)[0])

            if camel_case in (
                "SimulatorScenarios",
                "TrainerScenarios",
                "CalibratorScenarios",
            ):
                self.load_dataframe(file_name, camel_case)

    def load_dataframe(self, df_info: Union[str, "DataFrameInfo"], df_name=""):
        """
        Load a data frame from table file.

        :df_info: The file name of that containing the data frame, or pass a `DataFrameInfo`
        """
        from .data_loader import DataFrameInfo

        assert self.manager is not None, MelodieExceptions.MLD_INTL_EXC
        assert self.manager.data_loader is not None, MelodieExceptions.MLD_INTL_EXC
        if isinstance(df_info, str):
            df_name = (
                df_name
                if df_name != ""
                else os.path.splitext(os.path.basename(df_info))[0]
            )
            info = DataFrameInfo(df_name, {}, df_info)
            return self._load_dataframe(info)
        else:
            return self._load_dataframe(df_info)

    def load_matrix(
        self, mat_info: Union[str, "MatrixInfo"], mat_name=""
    ) -> np.ndarray:
        """
        Load a matrix from table file.

        :mat_info: The file name of that containing the matrix, or pass a `DataFrameInfo`
        """
        from .data_loader import MatrixInfo

        assert self.manager is not None, MelodieExceptions.MLD_INTL_EXC
        assert self.manager.data_loader is not None, MelodieExceptions.MLD_INTL_EXC
        if isinstance(mat_info, str):
            mat_name = mat_name if mat_name != "" else os.path.basename(mat_info)
            info = MatrixInfo(mat_name, None, mat_info)
            return self.manager.data_loader._load_matrix(info)
        else:
            return self.manager.data_loader._load_matrix(mat_info)

    def setup(self):
        pass

    def register_dataframe(
        self, table_name: str, data_frame: "pd.DataFrame", data_types: dict = None
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
        self.registered_dataframes[table_name] = data_frame

    def clear_cache(self):
        """
        Clear all caches under caching directory.
        """
        if os.path.exists(self._cache_dir):
            shutil.rmtree(self._cache_dir)
            os.mkdir(self._cache_dir)
        else:
            logger.warning("Cache directory does not exist!")

    @property
    def _cache_dir(self):
        return os.path.join(self.config.temp_folder, "cache", "pd-df")

    def _load_dataframe_cached(
        self, file_path_abs: str, disable_cache: bool
    ) -> "pd.DataFrame":
        """
        Load dataframe from file
        """

        def original_read_method(filename: str) -> pd.DataFrame:
            _, ext = os.path.splitext(filename)
            if ext in {".xls", ".xlsx"}:
                return pandas.read_excel(filename)
            elif ext in {".csv"}:
                return pandas.read_csv(filename)
            else:
                raise NotImplemented(file_path_abs)

        if self.config.input_dataframe_cache and not disable_cache:
            reader = PickledCacheFileReader(self._cache_dir, original_read_method)
            return reader.read(file_path_abs)
        else:
            return original_read_method(file_path_abs)

    def _load_dataframe(
        self, df_info: "DataFrameInfo", disable_cache=False
    ) -> "pd.DataFrame":
        """
        Register static table. The static table will be copied into database.

        The scenarios/agents parameter tables can also be registered by this method.

        :df_info: Target dataframe to load.
        :disable_cache: False by default. If true, this dataframe will be loaded from the original file
            even though the `Config.input_dataframe_cache` is set to `True`.
        :return: None
        """

        table: Optional["pd.DataFrame"]
        if df_info.df_name in self.registered_dataframes:
            return self.registered_dataframes[df_info.df_name]
        assert df_info.file_name is not None
        file_path_abs = os.path.join(self.config.input_folder, df_info.file_name)

        table = self._load_dataframe_cached(file_path_abs, disable_cache)

        self.registered_dataframes[df_info.df_name] = table

        return table

    def _load_matrix(
        self, matrix_info: "MatrixInfo", disable_cache=False
    ) -> "np.ndarray":
        """
        Register static matrix.

        :return: None
        """
        if matrix_info.mat_name in self.registered_matrices:
            return self.registered_matrices[matrix_info.mat_name]

        assert matrix_info.file_name is not None
        _, ext = os.path.splitext(matrix_info.file_name)
        file_path_abs = os.path.join(self.config.input_folder, matrix_info.file_name)

        def matrix_loader(filename: str) -> np.ndarray:
            if ext in {".xls", ".xlsx"}:
                table: "pd.DataFrame" = pd.read_excel(filename, header=None)
            elif ext in {".csv"}:
                table: "pd.DataFrame" = pd.read_csv(filename, header=None)
            else:
                raise NotImplementedError(
                    f"Cannot load file with extension {ext} to matrix."
                )
            return table.to_numpy(matrix_info.dtype, copy=True)

        if self.config.input_dataframe_cache and not disable_cache:
            array = PickledCacheFileReader(self._cache_dir, matrix_loader).read(
                file_path_abs
            )
        else:
            array = matrix_loader(file_path_abs)
        self.registered_matrices[matrix_info.mat_name] = array
        return array

    def dataframe_generator(
        self,
        df_info: Union[str, DataFrameInfo],
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
        scenarios_dataframe = TableInterface(scenarios_dataframe)
        cols = [col for col in scenarios_dataframe.columns]
        scenarios: List[Scenario] = []
        for i, row in enumerate(scenarios_dataframe.iter_dicts()):
            scenario = self.scenario_cls()
            scenario.manager = self.manager

            scenario._setup(row)
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
        if manager_type not in {"Simulator", "Trainer", "Calibrator"}:
            raise MelodieExceptions.Program.Variable.VariableNotInSet(
                "manager_type", manager_type, {"Simulator", "Trainer", "Calibrator"}
            )

        df_name = f"{manager_type}Scenarios"

        if df_name in self.registered_dataframes:
            return self.generate_scenarios_from_dataframe(df_name)
        elif underline_to_camel(df_name) in self.registered_dataframes:
            return self.generate_scenarios_from_dataframe(underline_to_camel(df_name))
        else:
            raise NotImplementedError(
                f"{manager_type}/{underline_to_camel(df_name)} is not supported! Registered tables are: {list(self.registered_dataframes.keys())}"
            )
