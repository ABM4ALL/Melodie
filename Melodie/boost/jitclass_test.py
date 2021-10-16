# -*- coding:utf-8 -*-
# @Time: 2021/10/8 9:35
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: jitclass_test.py
import time

import numba
import numpy as np
from numba import int32, float32  # import the types
from numba.experimental import jitclass
from numba import typed

spec = [
    ('value', int32),  # a simple scalar field
    ('array', float32[:]),  # an array field
]


@jitclass(spec)
class Bag(object):
    def __init__(self, value):
        self.value = value
        self.array = np.zeros(value, dtype=np.float32)

    @property
    def size(self):
        return self.array.size

    def increment(self, val):
        for i in range(self.size):
            self.array[i] += val
        return self.array

    @staticmethod
    def add(x, y):
        return x + y


class BagPlain(object):
    def __init__(self, value):
        self.value = value
        self.array = [0] * value

    @property
    def size(self):
        return self.array.size

    def increment(self, val):
        for i in range(len(self.array)):
            self.array[i] += val
        # return self.array

    @staticmethod
    def add(x, y):
        return x + y


N = 10_0000
BAGNUM = 100


@numba.njit
def create_numba_bags():
    b_lst = []
    for i in range(BAGNUM):
        b_lst.append(Bag(i))
    return b_lst


@numba.jit(nopython=True)
def f_a(bags):
    for i in range(N):
        for b in bags:
            b.increment(0)


def f_b(bags):
    t0 = time.time()
    for i in range(N):
        for b in bags:
            b.increment(1)

    t1 = time.time()
    return t1 - t0


mybag = Bag(1)
mybag.increment(0)

plain_bags = [BagPlain(1) for i in range(BAGNUM)]
# jit_bags = typed.List(create_numba_bags())
jit_bags = typed.List(create_numba_bags())

t0 = time.time()
f_a(jit_bags)
t1 = time.time()
print(t1 - t0)
print(f_b(plain_bags))
