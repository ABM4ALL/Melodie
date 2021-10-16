# cython:language_level=3
# -*- coding:utf-8 -*-
# @Time: 2021/10/3 20:58
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: test.pyx
#
# from cpython.ref cimport PyObject  # somewhere at the top
from cpython cimport PyObject_GetAttr, PyObject_GetAttrString, \
    PyObject_GetItem, PyList_GetItem, PyList_Size, PyObject_SetAttr, \
    PyObject_Call

cimport cython

def _apply_func_call(object lst, object call):
    cdef Py_ssize_t length
    cdef object obj2
    cdef object kwarg
    # cdef PyListObject l
    kwarg = {}
    length = PyList_Size(lst)
    l = <list> lst
    for i in range(length):
        # obj2 = <object> PyList_GetItem(lst, <Py_ssize_t> (i))
        PyObject_Call(call,
                      (<object> PyList_GetItem(lst, <Py_ssize_t> (i)),),
                      kwarg)
# cdef class CellCache:
#     cdef object[:] cache
#     cpdef __init__(self,length):
#         self.cache = [None for i in range(length)]
#
#     cpdef memorize_cache(self,object lst, object property):
#         cdef Py_ssize_t length
#         cdef object obj2
#         cdef object kwarg
#         kwarg = {}
#         length = PyList_Size(lst)
#         for i in range(length):
#             obj2 = <object> PyList_GetItem(lst, <Py_ssize_t> (i))
#             self.cache[i] = obj2
#     cpdef apply_cache(self,object lst,object property):
#         cdef Py_ssize_t length
#         cdef object obj2
#         cdef object kwarg
#         kwarg = {}
#         length = PyList_Size(lst)
#         for i in range(length):
#             # obj2 = <object> PyList_GetItem(lst, <Py_ssize_t> (i))
#             self.cache[i] = object

def apply_func_call(object lst, object call):
    return _apply_func_call(lst, call)
#
cdef class FastAttrClass:
    cdef object object1
    cdef object object2
    cdef object object3
    cdef object object4
    cdef object object5

    def __init__(self):
        self.object1 = <object> 1
        self.object2 = <object> 2

    def __getattribute__(self, item):
        return self.object1

    def __setattr__(self, key, value):
        self.object1 = value
