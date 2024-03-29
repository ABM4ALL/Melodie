import os
from typing import TYPE_CHECKING, Any, Dict, Literal, Optional

from MelodieInfra.db.base import SQLITE_FILE_SUFFIX
from MelodieInfra.db.db_configs import (
    BaseMelodieDBConfig,
    DBConfigTypes,
    SQLiteDBConfig,
)


class Config:
    """
    The configuration class of Melodie
    Config is needed by Simulator/Calibrator/Trainer and MelodieStudio for determining the project root,
    IO directories or other crucial configurations.
    """

    def __init__(
        self,
        project_name: str,
        project_root: str,
        input_folder: str,
        output_folder: str,
        visualizer_entry: str = "",
        data_output_type: Literal["csv", "sqlite"] = "csv",
        database_config: Optional["DBConfigTypes"] = None,
        input_cache: bool = False,
        **kwargs,
    ):
        self.project_name = project_name
        self.project_root = project_root
        self.output_folder = self.setup_folder_path(output_folder)
        self.input_folder = self.setup_folder_path(input_folder)
        self.temp_folder = ".melodie"

        self.studio_port = kwargs.get("studio_port", 8089)
        self.visualizer_port = kwargs.get("visualizer_port", 8765)
        self.parallel_port = kwargs.get("parallel_port", 12233)
        self.data_output_type = data_output_type

        if database_config is None:
            self.database_config = SQLiteDBConfig(
                os.path.join(self.output_folder,
                             self.project_name + SQLITE_FILE_SUFFIX)
            )
        else:
            assert isinstance(database_config, BaseMelodieDBConfig), (
                f"parameter database_config is {database_config},"
                f" not a valid data base configuration class. "
            )
            self.database_config = database_config

        if not os.path.exists(visualizer_entry) and visualizer_entry != "":
            raise FileNotFoundError(
                f"Visualizer entry file {visualizer_entry} is defined, but not found. "
            )
        self.visualizer_entry = visualizer_entry
        self.visualizer_tmpdir = os.path.join(self.temp_folder, "visualizer")
        self.input_dataframe_cache = input_cache
        self.init_temp_folders()

        self.setup()

    def init_temp_folders(self):
        if not os.path.exists(self.temp_folder):
            os.makedirs(self.temp_folder)
        if not os.path.exists(self.visualizer_tmpdir):
            os.makedirs(self.visualizer_tmpdir)

    def setup_folder_path(self, folder_path):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        return folder_path

    def setup(self):
        pass

    def to_dict(self):
        d = {k: v for k, v in self.__dict__.items()}
        d["database_config"] = self.database_config.to_json()
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]):
        db_conf = BaseMelodieDBConfig.from_json(d["database_config"])
        c = Config(
            d["project_name"],
            d["project_root"],
            d["input_folder"],
            d["output_folder"],
            database_config=db_conf,
        )
        return c

    def output_tables_path(self):
        """
        Get the path to store the tables output from the model. It is `data/output/{project_name}`

        If output to database and using sqlite, the output directory will be `data/output`
        """
        return os.path.join(self.output_folder)
