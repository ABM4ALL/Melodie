import logging
import os
import sqlite3
import sqlalchemy
import time
from typing import Union, Dict, TYPE_CHECKING, List, Tuple, Type, Hashable, Optional

from sqlalchemy.exc import OperationalError

from Melodie import Config
import pandas as pd

import numpy as np

from Melodie.basic import MelodieExceptions

if TYPE_CHECKING:
    from Melodie.scenario_manager import Scenario

TABLE_DTYPES = Dict[str, Union[str, Type[str], Type[float], Type[int], Type[complex], Type[bool], Type[object]]]

logger = logging.getLogger(__name__)


class DB:
    table_dtypes: Dict[str, TABLE_DTYPES] = {}
    EXPERIMENTS_TABLE = 'melodie_experiments'
    SCENARIO_TABLE = 'scenarios'
    ENVIRONMENT_RESULT_TABLE = 'env_result'

    RESERVED_TABLES = {'scenarios', 'env_result'}

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
            self.connection = self.create_connection(db_name)
            # self.connection
        else:
            raise NotImplementedError

    def get_engine(self):
        return self.connection

    def create_connection(self, database_name) -> sqlalchemy.engine.Engine:

        # conn = sqlite3.connect(os.path.join(self.db_path, database_name + ".sqlite"))
        # if database_name == "":
        #     return sqlalchemy.create_engine(f'sqlite://', echo=False)
        # else:
        return sqlalchemy.create_engine(f'sqlite:///{os.path.join(self.db_path, database_name + ".sqlite")}')
        # engine.
        # conn.execute("PRAGMA synchronize = OFF")
        # conn.execute("PRAGMA jorunal_mode = MEMORY")
        # conn.commit()
        # return engine

    @classmethod
    def register_dtypes(cls, table_name: str, dtypes: TABLE_DTYPES):
        """
        Register data types of a table for sqlalchemy.

        :return:
        """
        assert isinstance(dtypes, dict)
        if table_name in cls.table_dtypes:
            raise ValueError(f"Table dtypes of '{table_name}' has been already defined!")
        cls.table_dtypes[table_name] = dtypes

    @classmethod
    def get_table_dtypes(cls, table_name: str) -> TABLE_DTYPES:
        """
        Get the data type of a table.
        If table data type is not specified, return an empty dict.
        :param table_name:
        :return:
        """
        if table_name in cls.table_dtypes:
            return cls.table_dtypes[table_name]
        else:
            return {}

    def close(self):
        """
        Close DB connection.
        :return:
        """
        self.connection.dispose()

    def clear_database(self):
        """
        Clear the database, deleting all tables.
        :return:
        """
        logger.info(f"Database contains tables: {self.connection.table_names()}")

        for table_name in self.connection.table_names():
            self.connection.execute(f"drop table {table_name}")
            logger.info(f"Table '{table_name}' in database has been droped!")


    # def init_experiment(self, run_id_list: List[Tuple[int, int]]):
    #     self.drop_table(self.EXPERIMENTS_TABLE)
    #     self.create_table_if_not_exists(self.EXPERIMENTS_TABLE,
    #                                     {"run_id": "INTEGER", "scenario_id": "INTEGER", "status": "TEXT"})
    #     cur = self.connection.cursor()
    #     runs_list = []
    #     for run in run_id_list:
    #         runs_list.append((run[0], run[1], "BEFORE RUN"))
    #     cur.executemany("insert into")

    def table_exists(self, table_name: str) -> bool:
        sql = f"""SELECT * FROM sqlite_master WHERE type="table" AND name = '{table_name}'; """
        self.connection.execute(sql)
        self.connection.commit()
        res = self.connection.cursor().fetchall()
        return len(res) > 0

    def _dtype(self, a) -> str:
        if isinstance(a, int):
            return 'INTEGER'
        elif isinstance(a, float):
            return 'REAL'
        elif isinstance(a, str):
            return 'TEXT'
        elif np.issubdtype(a, np.integer):
            return 'INTEGER'
        elif np.issubdtype(a, np.floating):
            return 'REAL'
        else:
            raise ValueError(f'{a}, type {type(a)} not recognized!')

    def auto_convert(self, a: np.float) -> str:
        if isinstance(a, (int, float, str)):
            return a
        elif np.issubdtype(a, np.integer):
            return a.item()
        elif np.issubdtype(a, np.floating):
            return a.item()
        else:
            raise TypeError(f'{a},type {type(a)} not recognized!')

    def create_table_if_not_exists(self, table_name: str, dtypes: Dict[str, str]) -> bool:
        s = ''
        for key, dtype in dtypes.items():
            s += f'{key} {dtype},'
        s = s.strip(',')
        sql = f"""create table {table_name} ({s});"""
        try:
            self.connection.execute(sql)
            self.connection.commit()
            return True
        except sqlite3.OperationalError:  # Table exists, unable to create
            return False

    def batch_insert(self, table: str, records: List[Dict[str, Union[int, str, float]]]):
        """
        Batch insert records into sqlite data!
        :param records:
        :return:
        """
        t0 = time.time()
        records_to_insert = []
        key_names_list = list(records[0].keys())
        assert len(records) > 0
        key_names = ''
        value_names = ''
        for key in key_names_list:
            key_names += f'{key},'
            value_names += '?,'
        key_names = key_names.strip(',')
        value_names = value_names.strip(',')
        sql = f'insert into {table} ({key_names}) values ({value_names})'
        for record in records:
            records_to_insert.append([self.auto_convert(record[k]) for k in key_names_list])

        dtypes = {k: self._dtype(records[0][k]) for k in key_names_list}
        t1 = time.time()
        print(t1 - t0)
        self.create_table_if_not_exists(table, dtypes)

        cursor = self.connection.cursor()
        cursor.executemany(sql, records_to_insert)
        self.connection.commit()
        self.connection.close()

    def write_dataframe(self, table_name: str, data_frame: pd.DataFrame,
                        data_type: Optional[TABLE_DTYPES] = None,
                        if_exists='append'):
        """
        Write a dataframe to database.

        :param table_name: table_name
        :param data_frame:
        :param data_type: The data type for columns.
        :param if_exists: {'replace', 'fail', 'append'}
        :return:
        """
        if data_type is None:
            data_type = DB.get_table_dtypes(table_name)
        logger.info(f"datatype of table `{table_name}` is: {data_type}")
        data_frame.to_sql(table_name, self.connection, index=False, dtype=data_type, if_exists=if_exists)

    def read_dataframe(self, table_name: str) -> pd.DataFrame:
        """
        Read a table and return all content as a dataframe.
        :param table_name:
        :return:
        """
        try:
            return pd.read_sql(f'select * from {table_name}', self.connection)
        except OperationalError as e:
            raise MelodieExceptions.Data.AttemptingReadingFromUnexistedTable(table_name)

    def drop_table(self, table_name: str):
        """
        Drop table if it exists.
        :param table_name:
        :return:
        """
        self.connection.execute(f'drop table if exists  {table_name} ;')

    def query(self, sql) -> pd.DataFrame:
        """
        Execute sql command and return the result by pd.DataFrame.
        :param sql:
        :return:
        """
        return pd.read_sql(sql, self.connection)

    def paramed_query(self, table_name: str, conditions: Dict[str, Union[int, str, tuple, float]]) -> pd.DataFrame:
        conditions = {k: v for k, v in conditions.items() if v is not None}
        sql = f'select * from {table_name}'
        if len(conditions) > 0:
            sql += ' where'
            conditions_count = 0
            for k, v in conditions.items():
                if conditions_count == 0:
                    sql += f" {k}={v}"
                else:
                    sql += f" and {k}={v}"

                conditions_count += 1
        return self.query(sql)

    def query_scenarios(self, id: int = None):
        sql = f"select * from {self.SCENARIO_TABLE} "
        if id is not None:
            sql += f"where id={id}"
        return self.query(sql)

    def query_agent_results(self, agent_list_name: str, scenario_id: int = None, id: int = None, step: int = None):
        conditions = {'scenario_id': scenario_id, 'id': id, 'step': step}
        return self.paramed_query(agent_list_name, conditions)

    def query_env_results(self, scenario_id: int = None, step: int = None):
        conditions = {'scenario_id': scenario_id, 'step': step}
        return self.paramed_query(self.ENVIRONMENT_RESULT_TABLE, conditions)

    def delete_env_record(self, scenario_id: int, run_id: int):
        try:
            # cur = self.connection.cursor()
            self.connection.execute(
                f"delete from {self.ENVIRONMENT_RESULT_TABLE} where scenario_id={scenario_id} and run_id={run_id}")
        except sqlite3.OperationalError:
            import traceback
            traceback.print_exc()

    def delete_agent_records(self, table_name: str, scenario_id: int, run_id: int):
        try:
            cur = self.connection
            cur.execute(
                f"delete from {table_name} where scenario_id={scenario_id} and run_id={run_id}")
            # self.connection.commit()
        except sqlite3.OperationalError:
            import traceback
            traceback.print_exc()

    # def save_experiment_meta(self, scenario: 'Scenario'):
    #     d = scenario.toDict()
    #     d['finished_at'] = time.time()
    #     df = pd.DataFrame([
    #         d
    #     ])
    #     self.write_dataframe(self.EXPERIMENTS_TABLE, df, {}, "append")


def create_db_conn(config: 'Config' = None) -> DB:
    """
    create a Database by current config
    :return:
    """
    assert config is not None

    return DB(config.project_name, conn_params={'db_path': config.sqlite_folder})
