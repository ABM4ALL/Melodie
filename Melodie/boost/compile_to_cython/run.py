# -*- coding:utf-8 -*-
# @Time: 2021/10/29 10:38
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: run.py.py
import time
import random

from demo import helper

helper()


class A:
    def __init__(self):
        self.a = 0


def _helper_purepython(a):
    s = 0
    for i in range(100_00000):
        if random.random() > 0.5:
            s += 1
        else:
            s -= 1
    return s


def benchmark_purepython():
    s = 0
    a = A()
    for i in range(100_00000):
        a.a += 1
    return a


t1 = time.time()
benchmark_purepython()
t2 = time.time()
print(t2 - t1)
