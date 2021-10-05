# cython:language_level=3
# -*- coding:utf-8 -*-
# @Time: 2021/10/3 20:58
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: test.pyx.py
# from Cython.Includes.cpython.object import PyObject_SetAttr
from cpython.ref cimport PyObject  # somewhere at the top
from cpython cimport PyObject_GetAttr, PyObject_GetAttrString, \
    PyObject_GetItem, PyList_GetItem, PyList_Size, PyObject_SetAttr
cimport cython

cimport numpy as np
import numpy as np

def say_hello_to(name):
    print("Hello %s!" % name)

cdef class Cell:
    cdef int x
    cdef int y
    cpdef setpos(self, int x, int y):
        self.x = x
        self.y = y

    cpdef pos(self):
        print(self.x, self.y)

import sys

cell1 = Cell()
cdef get_cell_pos(Cell cell):
    cell.setpos(10, 20)
    print(cell.x, cell.y)

get_cell_pos(cell1)

python_dict = {"abc": 123}

python_list = [0, 1, 2, 3, 4]
position_list = [[cell1]]
python_dict_refcount = sys.getrefcount(python_dict)

cdef owned_reference(object obj, object attr):
    refcount = sys.getrefcount(python_dict)
    cdef object objref = <object> (0)
    #print(PyObject_HasAttr(obj, objref))
    cdef int i = 0
    for i in range(10000000):
        ret = PyList_GetItem(obj, <Py_ssize_t> (0))  # https://docs.python.org/3/c-api/list.html#c.PyList_SetItem
        #ret = PyObject_GetItem(obj, <object>(0))
        _att = PyObject_GetAttr(<object> ret, attr)
        ## print(ret)
    print("aaaaa", PyObject_GetItem(obj, objref))
    print('Inside owned_reference: {refcount}'.format(refcount=refcount))

cdef borrowed_reference(PyObject * obj):
    refcount = obj.ob_refcnt
    print('Inside borrowed_reference: {refcount}'.format(refcount=refcount))

cdef borrowed_reference2(PyObject * obj):
    refcount = obj.ob_refcnt
    cdef PyObject * objref = <PyObject *> ('__len__')
    print('Inside borrowed_reference: {refcount}'.format(refcount=refcount))

print('Initial refcount: {refcount}'.format(refcount=python_dict_refcount))
## owned_reference(python_dict)
borrowed_reference(<PyObject *> python_dict)

borrowed_reference2(<PyObject *> python_dict)

ctypedef np.int_t DTYPE_t

# @cython.boundscheck(False)
cpdef call_walk_position(object lst, object attr):
    cdef int x
    cdef int y
    cdef object inner_list
    cdef object obj2
    # cdef Cell c

    cdef Py_ssize_t dim1_size
    cdef Py_ssize_t dim2_size

    cdef np.ndarray[DTYPE_t, ndim=2] ret
    cdef int[:,:] result_view

    cdef object attr_val
    cdef PyObject* py_obj_ptr

    py_obj_ptr = <PyObject *>lst
    py_obj_ptr.ob_refcnt

    dim1_size = PyList_Size(lst)
    inner_list = <object> PyList_GetItem(lst, <Py_ssize_t> (0))
    dim2_size = PyList_Size(inner_list)
    ret = np.zeros([dim1_size, dim2_size], dtype=int)
    result_view = ret
    for i in range(dim1_size):
        inner_list = <object> PyList_GetItem(lst, <Py_ssize_t> (i))
        for j in range(dim2_size):
            obj2 = <object> PyList_GetItem(inner_list, <Py_ssize_t> (j))
            attr_val = <object> PyObject_GetAttr(obj2,attr)
            result_view[i][j] = <int> attr_val
    return ret

# @cython.boundscheck(False)
cpdef broadcast(object lst, object attr, np.ndarray new_attr):
    cdef int x
    cdef int y
    cdef object inner_list
    cdef object obj2
    # cdef Cell c

    cdef Py_ssize_t dim1_size
    cdef Py_ssize_t dim2_size

    # cdef np.ndarray[DTYPE_t, ndim=2] ret
    cdef int[:,:] new_attr_view

    cdef object attr_val
    cdef PyObject* py_obj_ptr

    new_attr_view = new_attr
    py_obj_ptr = <PyObject *>lst
    py_obj_ptr.ob_refcnt

    dim1_size = PyList_Size(lst)
    inner_list = <object> PyList_GetItem(lst, <Py_ssize_t> (0))
    dim2_size = PyList_Size(inner_list)


    for i in range(dim1_size):
        inner_list = <object> PyList_GetItem(lst, <Py_ssize_t> (i))
        for j in range(dim2_size):
            obj2 = <object> PyList_GetItem(inner_list, <Py_ssize_t> (j))
            PyObject_SetAttr(obj2,attr,<object> new_attr_view[i][j])


def call(d, attr):
    owned_reference(d, attr)
