# -*- coding:utf-8 -*-
# @Time: 2021/10/8 9:13
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: numbaextend_packed.py
from typing import Tuple

from numba import types


def get_type(name: str)->types.Type:
    class _CustomType(types.Type):
        def __init__(self):
            super(_CustomType, self).__init__(name=name)

    return _CustomType
