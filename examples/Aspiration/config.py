import os

from Melodie import Config

config = Config(
    project_name='Aspiration',
    project_root=os.path.dirname(__file__),
    sqlite_folder='data/sqlite',
    excel_source_folder='data/excel_source',
    output_folder='data/output',
)
