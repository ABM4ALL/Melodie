# -*- coding:utf-8 -*-
# @Time: 2021/10/6 21:56
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: test_test_features.py.py
import collections

# from Melodie.boost._test_features import apply_func_call
import dis
import time
import timeit
import numpy as np

np.array


class B:
    def __init__(self):
        self.b = 2
        self.c = 0.0


def f123test():
    N = 100_0000
    b = B()
    l = [B() for i in range(N)]
    d = {1: 1, 2: 2, 3: 3, 4: 4}
    l2 = [1, 2, 3, 4]
    # NT = collections.namedtuple('Point', ['b'])

    # p = b.b
    ret1 = timeit.timeit('d[1]', number=N, globals=locals())
    ret2 = timeit.timeit('l2[0]', number=N, globals=locals())
    print(ret1, ret2)
    t2 = time.time()


# f123test()


def f2():
    a = ''
    a.split
dis.dis(f2)
