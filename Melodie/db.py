import os
import sqlite3
from typing import Union, Dict, TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from Melodie.scenariomanager import Scenario
    from Melodie.config import Config


class DB:
    AGENT_PARAM_TABLE = 'agent_param'
    AGENT_RESULT_TABLE = 'agent_result'
    ENVIRONMENT_RESULT_TABLE = 'env_result'

    def __init__(self, db_name: str, db_type: str = 'sqlite', conn_params: Dict[str, str] = None):
        self.db_name = db_name
        assert db_type in {'sqlite'}
        if db_type == 'sqlite':
            if conn_params is None:
                conn_params = {'db_path': ''}
            elif not isinstance(conn_params, dict):
                raise NotImplementedError
            elif conn_params.get('db_path') is None:
                conn_params['db_path'] = ''

            self.db_path = conn_params['db_path']
            self.connection: sqlite3.Connection = self.create_connection(db_name)
        else:
            raise NotImplementedError

    def create_connection(self, database_name) -> sqlite3.Connection:
        conn = sqlite3.connect(os.path.join(self.db_path, database_name + ".sqlite"))
        return conn

    def close(self):
        self.connection.close()

    def createScenario(self, tableName: str, conn, scenario: 'Scenario', **kwargs):
        settingsDataFrame = pd.DataFrame([scenario.toDict()])
        settingsDataFrame.to_sql(tableName, conn, index=False, if_exists='replace', chunksize=1000,
                                 dtype=kwargs["dtype"])

    def create_scenario(self, table_name: str, scenario: 'Scenario'):
        settings_data_frame = pd.DataFrame([scenario.toDict()])
        settings_data_frame.to_sql(table_name, self.connection, index=False, if_exists='replace', chunksize=1000)

    def reset(self):
        self.drop_table(DB.AGENT_RESULT_TABLE)
        self.drop_table(DB.AGENT_PARAM_TABLE)
        self.drop_table(DB.ENVIRONMENT_RESULT_TABLE)

    def write_dataframe(self, table_name: str, data_frame: pd.DataFrame, if_exists='append'):
        data_frame.to_sql(table_name, self.connection, index=False, if_exists=if_exists, chunksize=1000)

    def read_dataframe(self, table_name: str) -> pd.DataFrame:
        return pd.read_sql(f'select * from {table_name}', self.connection)

    def drop_table(self, table_name: str):
        self.connection.execute(f'drop table if exists  {table_name} ;')


def create_db_conn() -> DB:
    """
    create a Database by current config
    :return:
    """
    from .run import get_config
    config = get_config()
    return DB(config.project_name, conn_params={'db_path': config.db_folder})
