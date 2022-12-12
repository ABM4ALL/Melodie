# -*- coding:utf-8 -*-
# @Time: 2022/11/24 23:01
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: db.py
import json
from typing import List

import pandas as pd
import sqlalchemy
from sqlalchemy.exc import OperationalError
from MelodieInfra.models import DatabaseQueryRequest, DataServiceStatus, DataServiceState, DatabaseBasicRequest


def get_table_names(conn_string: str) -> List[str]:
    """

    :return:
    """
    conn = sqlalchemy.create_engine(conn_string)
    table_names: List[str] = conn.table_names()
    return table_names


class DatabaseService():
    @staticmethod
    def query_database(req: DatabaseQueryRequest) -> DataServiceStatus:
        try:
            return DataServiceStatus(
                status=DataServiceState.SUCCESS,
                msg="Query Succeeded!",
                data=json.loads(DatabaseService.execute_sql(req.connection_string, req.sql).to_json(
                    orient="table", indent=4, index=False)),
            )
        except OperationalError as e:
            import traceback
            traceback.print_exc()
            return DataServiceStatus(
                status=DataServiceState.ERROR,
                msg=f"{e}",
                data=None
            )

    @staticmethod
    def table_names(req: DatabaseBasicRequest):
        try:
            return DataServiceStatus(
                status=DataServiceState.SUCCESS,
                msg="Get table names succeeded!",
                data=get_table_names(req.connection_string)
            )
        except OperationalError as e:
            import traceback
            traceback.print_exc()
            return DataServiceStatus(
                status=DataServiceState.ERROR,
                msg=f"{e}",
                data=None
            )

    @staticmethod
    def execute_sql(conn_string, sql: str):
        engine = sqlalchemy.create_engine(conn_string)
        return pd.read_sql(sql, engine)
