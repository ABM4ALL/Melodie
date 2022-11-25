# -*- coding:utf-8 -*-
# @Time: 2022/11/24 23:06
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: test_db.py.py
import os

import pytest

from MelodieInfra.services.database import DatabaseService
from tests.config import resources_path, skip_env_dependent


def test_read_sqlite():
    path = os.path.join(resources_path, r"db\test.sqlite")
    conn_string = f"sqlite:///{path}"
    resp = DatabaseService.execute_sql(conn_string, "select * from simulator_scenarios")
    print(resp)
    print(resp.to_json())


@pytest.mark.skipif(skip_env_dependent, reason="Mysql connection is ignored!")
def test_read_mysql():
    resp = DatabaseService.execute_sql("mysql+pymysql://root:123456@127.0.0.1/monitor_data?charset=utf8mb4",
                                       "show tables;")
    print(resp.iloc[:, 0].tolist())
