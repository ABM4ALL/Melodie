# -*- coding:utf-8 -*-
# @Time: 2021/12/1 9:15
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: utils.py
from typing import ClassVar, List, Tuple


def dtype_detect(spot_cls: type, args: Tuple) -> List[Tuple[str, str]]:
    spot = spot_cls(*args)
    spot.setup()

    dtypes: List[Tuple[str, str]] = []
    user_defined_spot_attr_names: List[str] = []
    for attr_name, attr_value in spot.__dict__.items():
        user_defined_spot_attr_names.append(attr_name)
        if isinstance(attr_value, (int, bool)):
            dtypes.append((attr_name, 'i8'))
        elif isinstance(attr_value, float):
            dtypes.append((attr_name, 'f8'))
        elif attr_name == 'scenario':
            continue
        else:
            raise TypeError(f'Unsupported Spot attribute "{attr_name}" with value {attr_value} ')
    return dtypes
