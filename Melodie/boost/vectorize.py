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


def py_gather_2d(list_2d: List[List[Union[int, float]]], property_name: str) -> np.ndarray:
    xmax, ymax, new_arr = preprocess(list_2d, property_name)
    for x in range(xmax):
        for y in range(ymax):
            new_arr[x][y] = getattr(list_2d[x][y], property_name)
    return new_arr


def py_broadcast_2d(list_2d: List[List[Union[int, float]]], property_name: str, property: np.ndarray) -> np.ndarray:
    ymax = len(list_2d[0])
    xmax = len(list_2d)
    assert xmax, ymax > 0
    for x in range(xmax):
        for y in range(ymax):
            setattr(list_2d[x][y], property_name, property[x][y].item())


try:
    from ._vectorize import broadcast_float, broadcast_int, gather_int, gather_float


    def c_gather_2d(list_2d: List[List[Union[int, float]]], property_name: str) -> np.ndarray:
        ymax = len(list_2d[0])
        xmax = len(list_2d)
        assert xmax, ymax > 0
        val = getattr(list_2d[0][0], property_name)
        if isinstance(val, int):
            return gather_int(list_2d, property_name)
        elif isinstance(val, float):
            return gather_float(list_2d, property_name)
        else:
            raise TypeError


    def c_broadcast_2d(list_2d: List[List[Union[int, float]]], property_name: str, property: np.ndarray):
        ymax = len(list_2d[0])
        xmax = len(list_2d)
        assert xmax, ymax > 0
        val = getattr(list_2d[0][0], property_name)
        if isinstance(val, int):
            broadcast_int(list_2d, property_name, property)
        elif isinstance(val, float):
            broadcast_float(list_2d, property_name, property)
        else:
            raise TypeError
except ImportError as e:
    import traceback

    traceback.print_exc()
    c_gather_2d = None
    c_broadcast_2d = None
# c_gather_2d = None
# c_broadcast_2d = None
gather_2d = c_gather_2d if c_gather_2d is not None else py_gather_2d
broadcast_2d = c_broadcast_2d if c_broadcast_2d is not None else py_broadcast_2d
