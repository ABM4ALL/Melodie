import os
from typing import List


class Config:
    def __init__(self,
                 project_name: str,
                 project_root: str = '',
                 db_folder: str = '_database',
                 output_folder: str = 'output',
                 with_db: bool = True,  # if false, Melodie will never create or connect to a data
                 parameters_source: str = 'generate',
                 parameters_xls_file: str = '',
                 excel_source_folder: str = '',
                 static_xls_files: List[str] = None
                 ):
        self.excel_source_folder = os.path.abspath(excel_source_folder)
        assert os.path.exists(self.excel_source_folder)
        self.project_name = project_name
        assert self.project_name.isidentifier(), 'project_name should be a valid identifier'

        self.project_root = project_root
        if self.project_root != '':
            assert os.path.exists(project_root)

        self.with_db = with_db
        if with_db:
            self.db_folder = os.path.join(self.project_root, db_folder)
            if not os.path.exists(self.db_folder):
                os.mkdir(self.db_folder)
            self.output_folder = os.path.join(self.project_root, output_folder)
            if not os.path.exists(self.output_folder):
                os.mkdir(self.output_folder)

        assert parameters_source in {'generate', 'from_file', 'from_database'}
        self.parameters_source = parameters_source
        if parameters_source == 'from_file':
            pass
            # assert os.path.exists(parameters_xls_file), f'File {parameters_xls_file} does not exist!'
            # self.parameters_xls_file = parameters_xls_file
            # self.static_xls_files = [] if static_xls_files is None else static_xls_files


class NewConfig:
    def __init__(self,
                 project_name: str,
                 project_root: str,
                 sqlite_folder: str,
                 excel_source_folder: str,
                 output_folder: str):
        pass
