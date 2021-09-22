import os
import sqlite3
from typing import Union, Dict, TYPE_CHECKING

import pandas as pd


if TYPE_CHECKING:
    from Melodie.scenariomanager import Scenario


class DB:
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

    # def read_DataFrame(self, table_name, conn, **kwargs):
    #     if len(kwargs) > 0:
    #         condition_temp = " where "
    #         for key, value in kwargs.items():
    #             condition_temp = condition_temp + key + " == '" + str(value) + "' and "
    #         condition = condition_temp[0:-5]
    #         DataFrame = pd.read_sql('select * from ' + table_name + condition, con=conn)
    #     else:
    #         DataFrame = pd.read_sql('select * from ' + table_name, con=conn)
    #     return DataFrame
    #
    # def write_DataFrame(self, table, table_name, column_names, conn, **kwargs):
    #     table_DataFrame = pd.DataFrame(table, columns=column_names)
    #     if "dtype" in kwargs:
    #         table_DataFrame.to_sql(table_name, conn, index=False,
    #                                if_exists='replace', chunksize=1000, dtype=kwargs["dtype"])
    #     else:
    #         table_DataFrame.to_sql(table_name, conn, index=False, if_exists='replace', chunksize=1000)
    #     return None
    #
    def createScenario(self, tableName: str, conn, scenario: 'Scenario', **kwargs):
        settingsDataFrame = pd.DataFrame([scenario.toDict()])
        settingsDataFrame.to_sql(tableName, conn, index=False, if_exists='replace', chunksize=1000,
                                 dtype=kwargs["dtype"])

    def create_scenario(self, table_name: str, scenario: 'Scenario'):
        settings_data_frame = pd.DataFrame([scenario.toDict()])
        settings_data_frame.to_sql(table_name, self.connection, index=False, if_exists='replace', chunksize=1000)

    def reset(self):
        self.drop_table('agent_params')
        self.drop_table('agent_results')

    def write_dataframe(self, table_name: str, data_frame: pd.DataFrame, if_exists='append'):
        data_frame.to_sql(table_name, self.connection, index=False, if_exists=if_exists, chunksize=1000)

    def read_dataframe(self, table_name: str) -> pd.DataFrame:
        return pd.read_sql(f'select * from {table_name}', self.connection)

    def drop_table(self, table_name: str):
        self.connection.execute(f'drop table if exists  {table_name} ;')
