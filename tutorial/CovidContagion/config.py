import os

from Melodie import Config

config = Config(
    project_name="CovidContagion",
    project_root=os.path.dirname(__file__),
    sqlite_folder="data/sqlite",
    excel_source_folder="data/input",
    output_folder="data/output",
)
