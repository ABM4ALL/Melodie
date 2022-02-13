# cython:language_level=3
# -*- coding:utf-8 -*-
# @Time: 2021/10/3 20:58
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: grid.pyx

import functools
from typing import ClassVar, Set, Dict, List, Tuple
from Melodie.agent import Agent
from cpython.ref cimport PyObject  # somewhere at the top
from cpython cimport PyObject_GetAttr, PyObject_GetAttrString, \
    PyObject_GetItem, PyList_GetItem, PyList_Size, PyObject_SetAttr
cimport cython
from libc.stdlib cimport rand, RAND_MAX
cimport numpy as np
import numpy as np

from libc.math cimport sin, cos, sqrt, log



cdef double uniform():
    return (rand()/(RAND_MAX*1.0))

cdef double box_muller(double mean, double sigma):
    cdef double pi = 3.1415926536
    cdef double x1, x2, y1
    x1 = uniform()
    x2 = uniform()
    y1 = sqrt(-2 * log(x1)) * cos(2 * pi * x2)
    # y2 = math.sqrt(-2 * math.log(x2)) * math.sin(2 * math.pi * x1)
    return y1

def rand_normal(mean, sigma):
    return box_muller(mean, sigma)


cdef class RandNormalGenerator:

    cdef double[:] cache
    cdef int pointer
    cdef int size
    def __init__(self, mean, sigma, size):
        self.cache = np.random.normal(mean, sigma, size=size)
        self.pointer = 0
        self.size = size
    
    def get(self):
        if self.pointer < self.size-1:
            self.pointer += 1
        else:
            self.pointer = 0
        return self.cache[self.pointer]