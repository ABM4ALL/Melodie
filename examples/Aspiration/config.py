import os

from Melodie import Config

config = Config(
    project_name='Aspiration_TrainerScenarios1',
    # project_name='Aspiration_TrainerScenariosHistorical',
    # project_name='Aspiration_TrainerScenariosSocial',
    project_root=os.path.dirname(__file__),
    sqlite_folder='data/sqlite',
    excel_source_folder='data/excel_source',
    output_folder='data/output',
)
