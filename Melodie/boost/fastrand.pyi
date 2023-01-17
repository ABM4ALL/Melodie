# cython:language_level=3
# -*- coding:utf-8 -*-
# @Time: 2021/10/3 20:58
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: grid.pyx

from ctypes import Union
from typing import List, TypeVar

T = TypeVar("T")


def sample(population: List[T], sample_num: int) -> List[T]: ...


def set_seed(seed: int) -> None: ...
