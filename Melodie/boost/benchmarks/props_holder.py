# -*- coding:utf-8 -*-
# @Time: 2022/9/4 10:47
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: test_props_holder.py
import time
from Melodie.boost.basics import PropHolder, foreach, length, times


class A:
    def __init__(self):
        self.a = 0


M = 10000000


def df_getitem_speed():
    holder = PropHolder()
    t0 = time.time()
    foreach()
    print("df:", time.time() - t0)


def atest2():
    s = 0
    a = A()
    t0 = time.time()
    for i in range(times):
        for j in range(length):
            a.a
            a.a = 123
    print("test2", time.time() - t0)


df_getitem_speed()
atest2()  # atest2
