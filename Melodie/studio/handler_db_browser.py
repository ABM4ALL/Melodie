# -*- coding:utf-8 -*-
# @Time: 2021/12/11 10:05
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: db.py

import json
import os.path
import tempfile
from typing import List

from flask import Blueprint, request
from Melodie.db import create_db_conn
from ._config import get_studio_config
from .messages import Response

db_browser = Blueprint('dbBrowser', __name__)


def read_sql(sql) -> dict:
    """
    Use pandas to read sql
    :param sql:
    :return:
    """
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        res = create_db_conn(config=get_studio_config()).query(sql)

        res.to_json(tf.name, orient='table', indent=4, index=False)
        data = tf.read()
        tf.close()
    return json.loads(data)


def get_table_names() -> List[str]:
    """

    :return:
    """
    conn = create_db_conn(get_studio_config())
    table_names: List[str] = conn.get_engine().table_names()
    return table_names


@db_browser.route('/query')
def db_browser_query():
    sql = request.args.get('sql')
    return Response.ok(read_sql(sql))


@db_browser.route('/tableNames')
def browse_sqlite():
    return Response.ok(get_table_names())
