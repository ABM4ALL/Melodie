import os
from typing import Any, Dict


class Config:
    """
    The configuration class of Melodie
    Config is needed by Simulator/Calibrator/Trainer and MelodieStudio for determining the project root, IO directories
     and other crucial configurations.
    """

    def __init__(
        self,
        project_name: str,
        project_root: str,
        sqlite_folder: str,
        excel_source_folder: str,
        output_folder: str,
        visualizer_entry: str = "",
    ):
        self.project_name = project_name
        self.project_root = project_root
        self.excel_source_folder = self.setup_folder_path(excel_source_folder)
        self.output_folder = self.setup_folder_path(output_folder)
        self.sqlite_folder = self.setup_folder_path(sqlite_folder)

        if not os.path.exists(visualizer_entry) and visualizer_entry != "":
            raise FileNotFoundError(
                f"Visualizer entry file {visualizer_entry} is defined, but not found. "
            )
        self.visualizer_entry = visualizer_entry
        self.setup()

    def setup_folder_path(self, folder_path):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        return folder_path

    def setup(self):
        pass

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(d: Dict[str, Any]):

        c = Config(
            d["project_name"],
            d["project_root"],
            d["sqlite_folder"],
            d["excel_source_folder"],
            d["excel_source_folder"],
            d["output_folder"],
        )
        return c
