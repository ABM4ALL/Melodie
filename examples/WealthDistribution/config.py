import os

from Melodie import Config

config = Config(
    project_name="WealthDistribution",
    project_root=os.path.dirname(__file__),
    input_folder="data/excel_source",
    output_folder="data/output",
)
