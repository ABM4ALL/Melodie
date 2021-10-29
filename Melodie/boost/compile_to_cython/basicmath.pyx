# -*- coding:utf-8 -*-
# @Time: 2021/10/29 11:25
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: basicmath.pyx.py

import cython
from libc.stdlib cimport atoi, rand, RAND_MAX

@cython.cfunc
@cython.cdivision(True)
@cython.locals(rand_int=cython.int, max_value=cython.int, r=cython.double)
@cython.returns(cython.double)
def fast_random():
    rand_int = rand()
    max_value = (RAND_MAX + 1)
    r = <double> rand_int / <double> max_value
    return r