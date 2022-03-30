# cython:language_level=3
# -*- coding:utf-8 -*-
# @Time: 2021/10/3 20:58
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: agent_list.pyx

from collections.abc import Sequence

cdef class SeqIter:
    """
    The iterator to deal with for-loops in AgentList or other agent containers
    """
    cdef int _i
    cdef list _seq

cdef class BaseAgentContainer():
    cdef int _id_offset
    cdef object scenario



cdef class AgentList(BaseAgentContainer):
    cdef int _iter_index
    # // cdef object scenario
    cdef object agent_class
    cdef int initial_agent_num
    cdef object model
    cdef list agents