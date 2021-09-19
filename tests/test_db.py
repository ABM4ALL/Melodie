# -*- coding:utf-8 -*-
# @Time: 2021/9/19 10:38
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: test_db.py
import os

from Melodie.db import DB


def test_create_db():
    db = DB('test')
    assert os.path.exists('test.sqlite')
    db.close()
    # os.remove('test.sqlite')

    db = DB('test', conn_params={'db_path': 'resources'})
    assert os.path.exists('resources/test.sqlite')
    db.close()
    # os.remove('resources/test.sqlite')
