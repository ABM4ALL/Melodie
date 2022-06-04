# -*- coding:utf-8 -*-
from typing import Union, List

import numpy as np

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


def c_apply(
    lst: List[List[Union[int, float]]], property_name: str, property: np.ndarray
):
    length = len(lst)
    assert length > 0
    val = getattr(lst[0], property_name)
    if isinstance(val, int):
        if property.dtype != np.int64:
            property = property.astype("int64")
        apply_int(lst, property_name, property)
    elif isinstance(val, float):
        if property.dtype != np.float64:
            property = property.astype("float64")
        apply_float(lst, property_name, property)
    else:
        raise TypeError


def c_vectorize_2d(
    list_2d: List[List[Union[int, float]]], property_name: str
) -> np.ndarray:
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


def c_apply_2d(
    list_2d: List[List[Union[int, float]]], property_name: str, property: np.ndarray
):
    ymax = len(list_2d[0])
    xmax = len(list_2d)
    assert xmax, ymax > 0
    val = getattr(list_2d[0][0], property_name)
    if isinstance(val, int):
        if property.dtype != np.int64:
            property = property.astype("int64")
        apply2d_int(list_2d, property_name, property)
    elif isinstance(val, float):
        if property.dtype != np.float64:
            property = property.astype("float64")
        apply2d_float(list_2d, property_name, property)
    else:
        raise TypeError


vectorize = c_vectorize
apply = c_apply
vectorize_2d = c_vectorize_2d
apply_2d = c_apply_2d
