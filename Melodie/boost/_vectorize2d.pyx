# cython:language_level=3
# -*- coding:utf-8 -*-


from cpython.ref cimport PyObject  # somewhere at the top
from cpython cimport PyObject_GetAttr, PyObject_GetAttrString, \
    PyObject_GetItem, PyList_GetItem, PyList_Size, PyObject_SetAttr
cimport cython

cimport numpy as np
import numpy as np

ctypedef np.int64_t DTYPE_t
ctypedef np.float64_t DTYPE_FLOAT

ctypedef fused DTYPE_FUSED:
    np.int64_t
    np.float64_t


cpdef vectorize2d_int(object lst, object attr):
    cdef int x
    cdef int y
    cdef object inner_list
    cdef object obj2

    cdef Py_ssize_t dim1_size
    cdef Py_ssize_t dim2_size

    cdef np.ndarray[DTYPE_t, ndim=2] ret
    cdef DTYPE_t[:,:] result_view

    cdef object attr_val
    cdef PyObject* py_obj_ptr

    py_obj_ptr = <PyObject *>lst
    py_obj_ptr.ob_refcnt

    dim1_size = PyList_Size(lst)
    inner_list = <object> PyList_GetItem(lst, <Py_ssize_t> (0))
    dim2_size = PyList_Size(inner_list)
    ret = np.zeros([dim1_size, dim2_size], dtype=np.int64)
    result_view = ret
    for i in range(dim1_size):
        inner_list = <object> PyList_GetItem(lst, <Py_ssize_t> (i))
        for j in range(dim2_size):
            obj2 = <object> PyList_GetItem(inner_list, <Py_ssize_t> (j))
            attr_val = <object> PyObject_GetAttr(obj2,attr)
            result_view[i][j] = <DTYPE_t> attr_val
    return ret

cpdef vectorize2d_float(object lst, object attr):
    cdef int x, y
    cdef object inner_list, obj2

    cdef Py_ssize_t dim1_size, dim2_size

    cdef np.ndarray[DTYPE_FLOAT, ndim=2] ret
    cdef DTYPE_FLOAT[:,:] result_view

    cdef object attr_val
    cdef PyObject* py_obj_ptr

    py_obj_ptr = <PyObject *>lst
    py_obj_ptr.ob_refcnt

    dim1_size = PyList_Size(lst)
    inner_list = <object> PyList_GetItem(lst, <Py_ssize_t> (0))
    dim2_size = PyList_Size(inner_list)
    ret = np.zeros([dim1_size, dim2_size], dtype=np.float64)
    result_view = ret
    for i in range(dim1_size):
        inner_list = <object> PyList_GetItem(lst, <Py_ssize_t> (i))
        for j in range(dim2_size):
            obj2 = <object> PyList_GetItem(inner_list, <Py_ssize_t> (j))
            attr_val = <object> PyObject_GetAttr(obj2,attr)
            result_view[i][j] = <DTYPE_FLOAT> attr_val
    return ret


cpdef apply2d_int(object lst, object attr, np.ndarray new_attr):
    cdef int x
    cdef int y
    cdef object inner_list
    cdef object obj2

    cdef Py_ssize_t dim1_size
    cdef Py_ssize_t dim2_size

    cdef DTYPE_t[:,:] new_attr_view

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
            PyObject_SetAttr(obj2, attr, <object> new_attr_view[i][j])

cpdef apply2d_float(object lst, object attr, np.ndarray new_attr):
    cdef int x
    cdef int y
    cdef object inner_list
    cdef object obj2

    cdef Py_ssize_t dim1_size
    cdef Py_ssize_t dim2_size

    cdef DTYPE_FLOAT[:,:] new_attr_view

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
