# -*- coding:utf-8 -*-
# @Time: 2021/10/21 10:46
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: loops.py
import random

import numpy as np


def constant_types_in_if():
    a = 123
    if a > 0:
        b = 1.234
        c = True
        d = "werqq"
        e = None


def constant_types_in_for_loop():
    for a in range(100):
        b = 1.234
        c = True
        d = "werqq"
        e = None


def container_types():
    l = [1, 2]
    m = {0: 1, 1: 2}
    s = {1, 2}


def assigning():
    s = {1, 2}
    x = s
    # a = s.pop(0)
    arr = np.array()
    arr2 = np.ndarray()
    arr3 = random.random()



def constant_types_with_args(a: int, b: float, c: bool, d: str, e: 'int'):
    pass
