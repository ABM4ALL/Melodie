import os
from typing import List

class Config:
    def __init__(self,
                 project_name: str,
                 project_root: str,
                 sqlite_folder: str,
                 excel_source_folder: str,
                 output_folder: str,
                 ):
        self.project_name = project_name
        self.project_root = project_root
        self.sqlite_folder = sqlite_folder

        if not os.path.exists(sqlite_folder):
            raise FileNotFoundError(
                f"sqlite_folder {sqlite_folder} of {self.__class__.__name__} was not found. Please create this folder.")

        self.excel_source_folder = excel_source_folder
        if not os.path.exists(excel_source_folder):
            raise FileNotFoundError(
                f"excel_source_folder {excel_source_folder} of {self.__class__.__name__} was not found. Please create this folder.")

        self.output_folder = output_folder
        if not os.path.exists(output_folder):
            raise FileNotFoundError(
                f"output_folder {output_folder} of {self.__class__.__name__} was not found. Please create this folder.")
