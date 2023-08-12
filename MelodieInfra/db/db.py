import logging
import os
from typing import Dict, TYPE_CHECKING, Optional, List, Tuple

import sqlalchemy
from sqlalchemy.exc import OperationalError
from sqlalchemy_utils import database_exists, create_database

from ..table import TableBase, TABLE_TYPE, GeneralTable, DatabaseConnector
from ..exceptions import MelodieExceptions

if TYPE_CHECKING:
    from MelodieInfra.config.config import Config

from .base import SQLITE_FILE_SUFFIX, TABLE_DTYPES

logger = logging.getLogger(__name__)


class DBConn:
    """
    DBConn provides API to write to/read from the database.

    """

    table_dtypes: Dict[str, TABLE_DTYPES] = {}
    existing_connections: Dict[str, "DBConn"] = {}
    SCENARIO_TABLE = "simulator_scenarios"
    ENVIRONMENT_RESULT_TABLE = "environment_result"

    def __init__(
        self,
        db_name: str,
        db_type: str = "sqlite",
        conn_params: Dict[str, str] = None,
        conn_string="",
    ):
        """
        :param db_name: Name of database file.
        :param db_type: Type of database, currently only support "sqlite".
        :param conn_params: A dict for connection parameters.
        """
        self.db_name = db_name

        if db_type not in {"sqlite", "mysql"}:
            MelodieExceptions.Data.InvalidDatabaseType(db_type, {"sqlite"})
        if db_type == "sqlite":
            if conn_params is None:
                conn_params = {"db_path": ""}
            elif not isinstance(conn_params, dict):
                raise NotImplementedError
            elif conn_params.get("db_path") is None:
                conn_params["db_path"] = ""

            self.db_path = conn_params["db_path"]
            self.connection = self.create_connection(db_name)
        else:
            raise NotImplementedError

    @staticmethod
    def from_connection_string(conn_string: str) -> "DBConn":
        """
        Create from connection string.

        :param conn_string:
        :return:
        """
        if conn_string in DBConn.existing_connections:
            return DBConn.existing_connections[conn_string]
        else:
            conn = DBConn("")
            conn.connection = sqlalchemy.create_engine(conn_string)
            DBConn.existing_connections[conn_string] = conn
            return conn

    def get_engine(self):
        """
        Get the connection

        :return: Database engine
        """
        return self.connection

    def create_connection(self, database_name) -> sqlalchemy.engine.Engine:
        """
        Create a connection to the sqlite database.

        :param database_name: Name of sqlite database file.
        :return:
        """
        return sqlalchemy.create_engine(
            f"sqlite:///{os.path.join(self.db_path, database_name + SQLITE_FILE_SUFFIX)}"
        )

    @classmethod
    def create_from_existing_db(self, type: str, meta: Dict):
        """
        Create from existing database

        :param type: Only support 'sqlite' now.
        :param meta: A dict like ``{'path': 'path-to-sqlite'}``
        :return: Database engine.
        """
        assert type in {"sqlite"}
        return sqlalchemy.create_engine(f"sqlite:///{os.path.join(meta['path'])}")

    @classmethod
    def register_dtypes(cls, table_name: str, dtypes: TABLE_DTYPES):
        """
        Register data types of a table for sqlalchemy.
        """
        MelodieExceptions.Assertions.Type("dtypes", dtypes, dict)
        if table_name in cls.table_dtypes:
            raise ValueError(
                f"Table dtypes of '{table_name}' has been already defined!"
            )
        cls.table_dtypes[table_name] = dtypes

    @classmethod
    def get_table_dtypes(cls, table_name: str) -> TABLE_DTYPES:
        """
        Get the data type of a table.
        If table data type is not specified, return an empty dict.

        :param table_name: Name of table in database.
        :return:
        """
        if table_name in cls.table_dtypes:
            return cls.table_dtypes[table_name]
        else:
            return {}

    def close(self):
        """
        Close DB connection.
        """
        self.connection.dispose()

    def clear_database(self):
        """
        Clear the database, deleting all tables.
        """
        if database_exists(self.connection.url):
            logger.info(f"Database contains tables: {self.connection.table_names()}.")
            table_names = list(self.connection.table_names())
            for table_name in table_names:
                self.connection.execute(f"drop table {table_name}")
            logger.info(f"Database drops tables: {table_names}.")
        else:
            create_database(self.connection.url)

    def write_dataframe(
        self,
        table_name: str,
        data_frame: TABLE_TYPE,
        data_types: Optional[TABLE_DTYPES] = None,
        if_exists="append",
    ):
        """
        Write a dataframe to database.

        :param table_name: Name of table.
        :param data_frame: The dataframe to be written into the database.
        :param data_types: The data type for columns.
        :param if_exists: A string in {'replace', 'fail', 'append'}.
        :return:
        """

        if isinstance(data_frame, TableBase):
            data_frame.to_database(self.connection, table_name)
        else:
            if data_types is None:
                data_types = DBConn.get_table_dtypes(table_name)
            logger.debug(f"datatype of table `{table_name}` is: {data_types}")
            data_frame.to_sql(
                table_name,
                self.connection,
                index=False,
                dtype=data_types,
                if_exists=if_exists,
            )

    def read_dataframe(
        self,
        table_name: str,
        id_scenario: Optional[int] = None,
        id_run: Optional[int] = None,
        conditions: List[Tuple[str, str]] = None,
        df_type: str = "pandas",
    ) -> "pd.DataFrame":
        """
        Read a table and return all content as a dataframe.

        For example:

        .. code-block:: python
            :linenos:

            df = create_db_conn(config).read_dataframe('agent_params', id_scenario=0,
                                                       conditions=[('id', "<=100"), ("health_state", '=1')])
            print(df)

        :param table_name: Name of table inside database.
        :param id_scenario: Filter of scenario
        :param id_run: Filter of run_id
        :param conditions: Custom conditions
        :param df_type: Type of dataframe, choose between "pandas" and "melodie-table"
        """
        assert df_type in {"pandas", "melodie-table"}

        where_condition_phrase = ""
        condition_phrases = []
        if conditions is not None:
            condition_phrases.extend([item[0] + item[1] for item in conditions])
        if id_scenario is not None:
            condition_phrases.append(f"id_scenario={id_scenario}")
        if id_run is not None:
            condition_phrases.append(f"id_run={id_scenario}")
        try:
            sql = f"select * from {table_name}"
            if len(condition_phrases) != 0:
                sql += " where " + " and ".join(condition_phrases)
            logger.debug("Querying database: " + sql)
            if df_type == "pandas":
                import pandas as pd

                return pd.read_sql(sql, self.connection)
            else:
                return GeneralTable.from_database(self.connection, table_name, sql)
        except OperationalError:
            import traceback

            traceback.print_exc()
            raise MelodieExceptions.Data.AttemptingReadingFromUnexistedTable(table_name)

    def drop_table(self, table_name: str):
        """
        Drop table if it exists.

        :param table_name: The name of table to drop.
        :return:
        """
        self.connection.execute(f"drop table if exists  {table_name} ;")

    def query(self, sql) -> "pd.DataFrame":
        """
        Execute sql command and return the result by pd.DataFrame.

        :param sql: SQL phrase to execute.
        :return:
        """
        import pandas as pd

        return pd.read_sql(sql, self.connection)


def create_db_conn(config: "Config") -> DBConn:
    """
    create a Database by current config

    :return: DBConn object.
    """
    return DBConn.from_connection_string(config.database_config.connection_string())


def get_sqlite_filename(config: "Config") -> str:
    """
    Get SQLite database filename from Melodie project config.
    """
    return os.path.join(config.output_folder, config.project_name + SQLITE_FILE_SUFFIX)
