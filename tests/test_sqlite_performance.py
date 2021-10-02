# -*- coding:utf-8 -*-
# @Time: 2021/9/27 8:07
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: test_sqlite_performance.py
import random
import sqlite3
import time

import logging

def test_sqlite_performance():
    logging.warning('performance test will not be executed!')
    return ''
    cx = sqlite3.connect("_database/test_performance.sqlite")
    cu = cx.cursor()
    # cu.execute('drop table if exists catalog ;')
    # cu.execute('create table catalog (id integer AUTO_INCREMENT,pid integer,name varchar(10), primary key (id))')
    cu.execute('PRAGMA synchronous = OFF;')
    for i in range(10):
        s = [(random.randint(0, 10000), 'name' + str(random.randint(0, 100))) for i in
             range(100_0000)]
        t0 = time.time()
        cu.executemany('insert into catalog (pid,name) values (?,?)', s)

        cx.commit()
        t1 = time.time()
        print(t1 - t0)


def test_select():
    logging.warning('performance test will not be executed!')
    return ''
    cx = sqlite3.connect("_database/test_performance.sqlite")
    cu = cx.cursor()
    # cu.execute('drop table if exists catalog ;')
    # cu.execute('create table catalog (id integer AUTO_INCREMENT,pid integer,name varchar(10), primary key (id))')
    # cu.execute('PRAGMA synchronous = OFF;')

    # s = [(random.randint(0, 10000), 'name' + str(random.randint(0, 100))) for i in
    #      range(100_0000)]
    t0 = time.time()
    ret = cu.execute('select * from catalog where name=\"name30\"')

    t1 = time.time()
    all = ret.fetchall()
    t2 = time.time()
    cx.commit()
    print(len(all))
    print(t1 - t0, t2 - t1)
    pass

