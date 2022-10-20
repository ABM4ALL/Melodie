# cython:language_level=3
# -*- coding:utf-8 -*-
# @Time: 2021/10/3 20:58
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: agent_list.pyx
from libcpp.unordered_map cimport unordered_map as cpp_map
from collections.abc import Sequence
from .basics cimport Agent
cdef class SeqIter:
    """
    The iterator to deal with for-loops in AgentList or other agent containers
    """
    cdef int _i
    cdef list _seq

cdef class DictIter:
    """
    The iterator to deal with for-loops in AgentDict or other agent containers
    """
    cdef object _iter
    cdef dict _dict

cdef class BaseAgentContainer():
    cdef int _id_offset
    cdef object scenario
    cpdef list init_agents(self) except *

    cdef object agent_class
    cdef int initial_agent_num
    cdef object model

cdef class AgentDict(BaseAgentContainer):
    cdef dict agents
    cpdef remove(self, Agent agent)
    cdef _add(self, Agent agent, dict params)
    cpdef Agent get_agent(self, long agent_id)

cdef class AgentList(BaseAgentContainer):
    cdef int _iter_index
    cdef public list agents

    cdef cpp_map[long, long]* indices     
    cdef cpp_map[long, long] _map

    cpdef _add(self, Agent agent, dict params)
    cpdef remove(self, Agent agent)

    # Unordered map is more efficient than cythonized binary search or python dict
    cpdef Agent get_agent(self, long agent_id)

    cdef long _get_index(self, long agent_id) except *
    cdef void _set_index(self, long agent_id, long index) except *

    # cpdef add_agent_id(self, long agent_id, long index)
    cpdef method_foreach(self, str method_name, tuple args) except *
    cpdef list init_agents(self) except *
    cpdef vectorize(self, str prop_name) except *
    cpdef list filter(self, condition) except *
    
cpdef test_container() except *