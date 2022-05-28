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


cpdef vectorize_int(object lst, object attr):
    cdef int x, y
    cdef object obj2

    cdef Py_ssize_t dim1_size

    cdef np.ndarray[DTYPE_t, ndim=1] ret
    cdef DTYPE_t[:] result_view

    cdef object attr_val
    cdef PyObject* py_obj_ptr

    py_obj_ptr = <PyObject *>lst
    py_obj_ptr.ob_refcnt

    length = PyList_Size(lst)
    ret = np.zeros(length, dtype=np.int64)
    result_view = ret
    for i in range(length):
        obj2 = <object> PyList_GetItem(lst, <Py_ssize_t> (i))
        attr_val = <object> PyObject_GetAttr(obj2,attr)
        result_view[i] = <DTYPE_t> attr_val
    return ret

cpdef vectorize_float(object lst, object attr):
    cdef int x, y
    cdef object obj2

    cdef Py_ssize_t dim1_size

    cdef np.ndarray[DTYPE_FLOAT, ndim=1] ret
    cdef DTYPE_FLOAT[:] result_view

    cdef object attr_val
    cdef PyObject* py_obj_ptr

    py_obj_ptr = <PyObject *>lst
    py_obj_ptr.ob_refcnt

    length = PyList_Size(lst)
    ret = np.zeros(length, dtype=np.float64)
    result_view = ret
    for i in range(length):
        obj2 = <object> PyList_GetItem(lst, <Py_ssize_t> (i))
        attr_val = <object> PyObject_GetAttr(obj2,attr)
        result_view[i] = <DTYPE_FLOAT> attr_val
    return ret

cpdef apply_int(object lst, object attr, np.ndarray new_attr):
    cdef int x
    cdef int y
    cdef object obj2

    cdef Py_ssize_t dim1_size

    cdef DTYPE_t[:] new_attr_view

    cdef object attr_val

    new_attr_view = new_attr
    dim1_size = PyList_Size(lst)
    for i in range(dim1_size):
        obj2 = <object> PyList_GetItem(lst, <Py_ssize_t> (i))
        PyObject_SetAttr(obj2, attr, <object> new_attr_view[i])

cpdef apply_float(object lst, object attr, np.ndarray new_attr):
    cdef int x, y
    cdef object obj2

    cdef Py_ssize_t dim1_size

    cdef DTYPE_FLOAT[:] new_attr_view

    cdef object attr_val

    new_attr_view = new_attr
    dim1_size = PyList_Size(lst)
    for i in range(dim1_size):
        obj2 = <object> PyList_GetItem(lst, <Py_ssize_t> (i))
        PyObject_SetAttr(obj2,attr,<object> new_attr_view[i])
