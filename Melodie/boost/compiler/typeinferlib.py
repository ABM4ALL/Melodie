# -*- coding:utf-8 -*-
# @Time: 2021/10/21 13:29
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: typeinferlib.py

import ast
import random
import sys
import logging
import time

import numpy as np
from typing import List, Dict, ClassVar, Set, Generic, TypeVar, Tuple

import pandas

from Melodie import Agent
from Melodie.grid import Grid

logging.basicConfig(level=logging.WARNING, stream=sys.stderr)
logger = logging.getLogger(__name__)

registered_types = {  # 保留类型或者可以直接求值的类型
    'int': int,
    'float': float,
    'str': str,
    'bool': bool,

    'Agent': Agent,
    'Grid': Grid,
}

global_names = {  # 导入的包名
    'np': np,
    'pd': pandas,
    'random': random,
    'time': time,
}

function_types = {  # 函数的返回类型

    np.array: np.ndarray,
    np.random.random: np.ndarray,
    np.random.randint: np.ndarray,
    np.sin: np.ndarray,

    random.random: float,
    random.randint: int,
}


# T = TypeVar('T')

# class ArrayOf
#
# class Array(Generic[T]):
#     _type = None
#
#     def __class_getitem__(cls, item):
#         cls._type = item
#         Generic[T].__class_getitem(cls, item)
#
#
# arr = Array[Agent]
# print(arr)

class ArrayOfAgents:
    pass


class assign:
    @staticmethod
    def _infer_from_value(target_id, node_value, types_inferred):
        if isinstance(node_value, ast.Constant):
            if node_value is None:
                raise NotImplementedError
            else:
                types_inferred[target_id] = type(node_value.value)

        elif isinstance(node_value, ast.Name):
            assert node_value.id in types_inferred, node_value.id
            types_inferred[target_id] = types_inferred[node_value.id]

        elif isinstance(node_value, ast.Call):
            func = node_value.func
            if isinstance(func, ast.Name):
                func_name = func.id
                if func_name in {'len', 'sum'}:
                    types_inferred[target_id] = int
                else:
                    raise NotImplementedError(func_name)
            elif isinstance(func, ast.Attribute):
                chain = attribute.get_chain(func)
                chain.reverse()
                called = attribute.get_out_type_from_attribute_chain(chain, types_inferred)
                if type(called) == type:  # if it is a class variable, e.g., np.ndarray
                    types_inferred[target_id] = called
                elif called in function_types:
                    types_inferred[target_id] = function_types[called]
                elif "return" in called.__annotations__:
                    types_inferred[target_id] = called.__annotations__['return']
                else:
                    raise TypeError(f"[Line: {node_value.lineno}]Cannot infer return value of function {called}. "
                                    f"Please register this function or type the left variable.")
            else:
                raise NotImplementedError(ast.dump(node_value))

        elif isinstance(node_value, ast.BinOp):
            types_inferred[target_id] = float
            logger.warning(f'Found binop at {ast.dump(node_value)}. Assigning the left value to np.float')
            return

        elif isinstance(node_value, (ast.List, ast.Set, ast.Dict)):
            if isinstance(node_value, ast.List):
                types_inferred[target_id] = list
            elif isinstance(node_value, ast.Set):
                types_inferred[target_id] = set
            elif isinstance(node_value, ast.Dict):
                types_inferred[target_id] = dict
            else:
                raise NotImplementedError

        else:
            types_inferred[target_id] = int
            logger.warning(f'ignored {ast.dump(node_value)}')
            print(f'ignored {ast.dump(node_value)}')
            return

    @staticmethod
    def infer_from_value(target_id, node_value, types_inferred):
        assign._infer_from_value(target_id, node_value, types_inferred)
        return types_inferred


class attribute:
    @staticmethod
    def get_chain(attr: ast.Attribute):
        attr_name_chain = []  # 名称链。意思是从右向左搜索方法的名称
        while isinstance(attr, ast.Attribute):
            attr_name_chain.append(attr.attr)
            attr = attr.value
        assert isinstance(attr, ast.Name)
        attr_name_chain.append(attr.id)
        return attr_name_chain

    @staticmethod
    def get_out_type_from_attribute_chain(chain: List[str], types_inferred):
        assert len(chain) > 1, chain
        if chain[0] in types_inferred:  # 寻找根对象。根对象可能是被注册的，或者已经被扫描过。
            value = types_inferred[chain[0]]
        elif chain[0] in global_names:
            value = global_names[chain[0]]
        else:
            raise TypeError
        index = 1
        while index < len(chain):
            value = getattr(value, chain[index])
            index += 1
        return value


def register_type(cls_var: ClassVar):
    registered_types[cls_var.__name__] = cls_var
    print(cls_var.__name__)
