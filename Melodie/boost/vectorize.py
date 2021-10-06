# -*- coding:utf-8 -*-
# @Time: 2021/10/5 14:04
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: vectorize.py
from typing import Union, List

import numpy as np


def preprocess(list_2d: List[List[Union[int, float]]], property_name: str):
    ymax = len(list_2d[0])
    xmax = len(list_2d)
    assert xmax, ymax > 0
    val = getattr(list_2d[0][0], property_name)
    if isinstance(val, int):
        arr = np.zeros((xmax, ymax))
    elif isinstance(val, float):
        arr = np.zeros((xmax, ymax))
    else:
        raise TypeError
    return xmax, ymax, arr


def py_vectorize_2d(list_2d: List[List[Union[int, float]]], property_name: str) -> np.ndarray:
    xmax, ymax, new_arr = preprocess(list_2d, property_name)
    for x in range(xmax):
        for y in range(ymax):
            new_arr[x][y] = getattr(list_2d[x][y], property_name)
    return new_arr


def py_apply_2d(list_2d: List[List[Union[int, float]]], property_name: str, property: np.ndarray) -> np.ndarray:
    ymax = len(list_2d[0])
    xmax = len(list_2d)
    assert xmax, ymax > 0
    for x in range(xmax):
        for y in range(ymax):
            setattr(list_2d[x][y], property_name, property[x][y].item())


try:
    from ._vectorize import apply_float, apply_int, vectorize_int, vectorize_float
    from ._vectorize2d import apply2d_float, apply2d_int, vectorize2d_int, vectorize2d_float


    def c_vectorize(lst: List[List[Union[int, float]]], property_name: str) -> np.ndarray:
        length = len(lst)
        assert length > 0
        val = getattr(lst[0], property_name)
        if isinstance(val, int):
            return vectorize_int(lst, property_name)
        elif isinstance(val, float):
            return vectorize_float(lst, property_name)
        else:
            raise TypeError


    def c_apply(lst: List[List[Union[int, float]]], property_name: str, property: np.ndarray):

        length = len(lst)
        assert length > 0
        val = getattr(lst[0], property_name)
        if isinstance(val, int):
            if property.dtype != np.int64:
                property = property.astype('int64')
            apply_int(lst, property_name, property)
        elif isinstance(val, float):
            if property.dtype != np.float64:
                property = property.astype('float64')
            apply_float(lst, property_name, property)
        else:
            raise TypeError


    def c_vectorize_2d(list_2d: List[List[Union[int, float]]], property_name: str) -> np.ndarray:
        ymax = len(list_2d[0])
        xmax = len(list_2d)
        assert xmax, ymax > 0
        val = getattr(list_2d[0][0], property_name)
        if isinstance(val, int):
            return vectorize2d_int(list_2d, property_name)
        elif isinstance(val, float):
            return vectorize2d_float(list_2d, property_name)
        else:
            raise TypeError


    def c_apply_2d(list_2d: List[List[Union[int, float]]], property_name: str, property: np.ndarray):
        ymax = len(list_2d[0])
        xmax = len(list_2d)
        assert xmax, ymax > 0
        val = getattr(list_2d[0][0], property_name)
        if isinstance(val, int):
            if property.dtype != np.int64:
                property = property.astype('int64')
            apply2d_int(list_2d, property_name, property)
        elif isinstance(val, float):
            if property.dtype != np.float64:
                property = property.astype('float64')
            apply2d_float(list_2d, property_name, property)
        else:
            raise TypeError
except ImportError as e:
    import traceback

    traceback.print_exc()
    c_vectorize_2d = None
    c_apply_2d = None

# vectorize_2d = c_vectorize_2d if c_vectorize_2d is not None else py_vectorize_2d
# apply_2d = c_apply_2d if c_apply_2d is not None else py_apply_2d
vectorize = c_vectorize
apply = c_apply
vectorize_2d = c_vectorize_2d
apply_2d = c_apply_2d
