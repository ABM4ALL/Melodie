# cython:language_level=3
# -*- coding:utf-8 -*-

import functools
from typing import Type, Set, Dict, List, Tuple
from cpython.ref cimport PyObject  # somewhere at the top
from cpython cimport PyObject_GetAttr, PyObject_GetAttrString, \
    PyObject_GetItem, PyList_GetItem, PyList_Size, PyObject_SetAttr
cimport cython
from libc.stdlib cimport rand, RAND_MAX, srand, malloc, free
cimport numpy as np
import numpy as np

from libc.math cimport sin, cos, sqrt, log, ceil
import random

from math import log as _log, exp as _exp, pi as _pi, e as _e, ceil as _ceil
from math import sqrt as _sqrt, acos as _acos, cos as _cos, sin as _sin
from os import urandom as _urandom

import random
import time
cimport numpy as np
import numpy as np
from cpython cimport array
import array

ctypedef np.int64_t DTYPE_t

srand(time.time())

cdef double uniform():
    return (rand()/(RAND_MAX*1.0))

@cython.cdivision(True)
cdef long randint(long _min, long _max):
    return  rand() % (_max-_min+1) + _min

cdef class ReservoirSample(object):
    cdef int _size
    cdef int _counter
    cdef long *_sample

    cdef void _initialize(self, int size):
        self._size = size
        self._counter = 0
        self._sample = <long *> malloc(size * sizeof(long))


    @cython.boundscheck(False)
    @cython.wraparound(False)
    cdef void feed(self, long item):
        cdef long rand_int
        self._counter += 1
        # The i.th element(i <= k) directly put into the pool
        if self._counter-1 < self._size:
            self._sample[self._counter-1] = item
            return
        # The i.th element (i > k) put into the pool with the possibility of k/i
        rand_int = randint(1, self._counter)
        if rand_int <= self._size:
            self._sample[rand_int - 1] = item

    cdef long* _get_samples(self):
        return self._sample


@cython.nonecheck(False)
cdef long* _reservoir_sample(int size, int num):
    """

    Return the pointer of reservoir array
    """
    cdef list sample
    cdef ReservoirSample rs
    cdef int item
    rs = ReservoirSample()
    rs._initialize(num)
    for item in range(size):
        rs.feed(item)
    return rs._get_samples()


cpdef list reservoir_sample(list population, int num):
    cdef int size = len(population)

    cdef long sample_index
    cdef long* samples = _reservoir_sample(size, num)
    cdef list result = [None] * num
    for i in range(num):
        sample_index = samples[i]
        result[i] = population[sample_index]
    free(samples)
        
    return result 

@cython.cdivision(True)
cdef double log_base(double x, double base):
    return log(x)/log(base)

cpdef object sample(list population, int sample_num):
    """
    Randomly sample `sample_num` agents from the container
    This code is the copied from standard library `random` and did some performance optimizations. 

    :param sample_num:
    :return:
    """
    
    cdef int k = sample_num
    cdef int n = len(population)
    cdef int setsize = 21        # size of a small set minus size of an empty list
    cdef list result
    cdef list pool  
    cdef int i, j

    # randbelow = random._inst._randbelow

    if not 0 <= k <= n:
        raise ValueError("Sample larger than population or is negative")
    result = [None] * k
    
    if k > 5:
        # setsize += 4 ** _ceil(_log(k * 3, 4)) # table size for big sets
        setsize += 4 ** <int>ceil(log_base(k * 3, 4)) # table size for big sets
    # print(n<=setsize)
    if n <= setsize:
        # # An n-length list is smaller than a k-length set
        # pool = list(population)
        # for i in range(k):         # invariant:  non-selected at [0,n-i)
        #     j = randbelow(n-i)
        #     result[i] = pool[j]
        #     pool[j] = pool[n-i-1]   # move non-selected item into vacancy
        return reservoir_sample(population, sample_num)
    else:
        selected = set()
        selected_add = selected.add
        for i in range(k):
            # j = randbelow(n)
            j = randint(0, n-1)
            while j in selected:
                # j = randbelow(n)
                j = randint(0, n-1)
            selected_add(j)
            # print(j)
            result[i] = population[j]
    return result