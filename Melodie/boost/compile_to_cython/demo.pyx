# cython:language_level=3
# -*- coding:utf-8 -*-
# @Time: 2021/10/29 9:53
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: demo.py.py
import time
import random
import cython
cimport basicmath
import numpy as np

def myfunction(x, y=2):
    a = x - y
    return a + x * y

def _helper_purepython(a):
    s = 0
    for i in range(100_00000):
        if random.random() > 0.5:
            s += 1
        else:
            s -= 1
    return s

@cython.cfunc
@cython.boundscheck(False)
@cython.returns(cython.int)
@cython.cdivision(True)
@cython.locals(a=cython.int, s=cython.int, r=cython.double, max=cython.double)
def _helper(a):
    s = 0
    for i in range(100_00000):
        r = basicmath.fast_random()
        if r > 0.3:
            s += 1
        else:
            s -= 1
    return s


@cython.cclass
class A:
    cython.declare(a=cython.int, b=cython.int)

    @cython.locals(b=cython.int)
    def __init__(self, b=0):
        self.a = 3
        self.b = b

    @cython.locals(x=cython.int, z=cython.int, i=cython.int)
    def foo(self, x):
        z = 0
        for i in range(1000):
            z += 1
        print(z)


@cython.cfunc
@cython.returns(A)
@cython.cdivision(True)
@cython.locals(s=cython.int, r=cython.double, max=cython.double)
def _benchmark():
    s = 0
    array_of_child = np.array([A() for i in range(100)], dtype=np.object_)
    # a = A()

    for i in range(100_00000):
        a = <A> array_of_child[0]
        a.a += 1
    return array_of_child[0]

@cython.ccall
def helper():
    t0 = time.time()
    s = _helper(0)
    print(s)
    t1 = time.time()
    _benchmark()
    t2 = time.time()
    print(t1 - t0, t2 - t1)
