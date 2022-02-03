# -*- coding:utf-8 -*-
# @Time: 2021/10/21 13:29
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: typeinferlib.py
import copy
from typing import Union, Dict, Any, Tuple
import ast
import random
import sys
import logging
import time

import astunparse
import numpy as np
from typing import List, ClassVar

import pandas
from pprintast import pprintast

logging.basicConfig(level=logging.WARNING, stream=sys.stderr)
logger = logging.getLogger(__name__)

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
    np.random.uniform: np.ndarray,
    np.sin: np.ndarray,

    random.random: float,
    random.randint: int,

}

try:
    from ..jitclasses import JITGrid, JITNetwork
    from Melodie import Grid, Network

    function_types[JITGrid] = Grid
    function_types[JITNetwork] = JITNetwork
except ImportError:
    import traceback

    traceback.print_exc()


def query_function_return_value_by_name(func_name: str) -> Tuple[Union[type, None], bool]:
    for f in function_types.keys():
        if f.__name__ == func_name:
            return function_types[f], True
    return None, False


def constant_annotation_to_ast(anno_str: str):
    anno: ast.Module = ast.parse(anno_str)
    body: List[ast.Expr] = anno.body
    assert len(body) == 1, pprintast(body)
    return body[0].value


def parse_annotation_str(anno_str: str):
    return parse_annotation_ast(constant_annotation_to_ast(anno_str))


def parse_annotation_ast(anno: Union[ast.Name, ast.Constant]) -> 'BoostTypeModel':
    """
    解析Annotation中的类型。
    :param anno:
    :return:
    """
    if type(anno) == ast.Constant:
        anno = constant_annotation_to_ast(anno.value)
    if isinstance(anno, ast.Name):
        if anno.id in registered_types:
            return registered_types[anno.id]
        else:
            logger.warning(f"Class {anno.id} is not registered!")
            return BoostTypeModel.undetermined()
    elif anno is None:
        raise TypeError("Do not use `None` as the type annotation!")
    elif isinstance(anno, ast.Attribute):
        return BoostTypeModel.from_type(eval(astunparse.unparse(anno)))
    elif isinstance(anno, ast.Subscript):
        assert isinstance(anno.value, ast.Name)
        slice: ast.Slice = anno.slice
        outer_name = anno.value.id
        inner_names = []
        if isinstance(slice.value, ast.Name):
            inner_names.append(slice.value.id)
        elif isinstance(slice.value, ast.Tuple):
            for name in slice.value.elts:
                inner_names.append(name.id)
        else:
            raise NotImplementedError
        btm = BoostTypeModel()
        btm.type_tree = {
            registered_types[outer_name].root: [registered_types[inner_name].root for inner_name in
                                                inner_names]}
        return btm
    else:
        raise NotImplementedError(anno)


def parse_annotation(annotation):
    """

    :param annotation:
    :return:
    """
    if isinstance(annotation, str):
        return parse_annotation_str(annotation)
    elif isinstance(annotation, ast.AST):
        return parse_annotation_ast(annotation)
    else:
        raise TypeError()


class BoostTypeModel:
    class UndeterminedType:
        pass

    def __init__(self):
        self.type_tree = {}

    @staticmethod
    def from_type(type) -> 'BoostTypeModel':
        btm = BoostTypeModel()
        btm.type_tree = {type: None}
        return btm

    @staticmethod
    def from_annotation(annotation: Union[str, ast.AST]) -> 'BoostTypeModel':
        btm = parse_annotation(annotation)
        assert isinstance(btm, BoostTypeModel)
        return btm

    @staticmethod
    def undetermined() -> 'BoostTypeModel':
        return BoostTypeModel.from_type(BoostTypeModel.UndeterminedType)

    @property
    def root(self):
        keys = list(self.type_tree.keys())
        return keys[0]

    def child_types(self) -> List[type]:
        return self.type_tree[self.root]

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.type_tree}>"

    def __eq__(self, other):
        if isinstance(other, type):
            return self.root == other
        else:
            return False

    # def


class assign:
    @staticmethod
    def _infer_from_value(target_id, node_value, types_inferred: Dict[str, BoostTypeModel]):
        if isinstance(node_value, ast.Constant):
            if node_value is None:
                raise NotImplementedError
            else:
                types_inferred[target_id] = BoostTypeModel.from_type(type(node_value.value))

        elif isinstance(node_value, ast.Name):
            assert node_value.id in types_inferred, node_value.id
            types_inferred[target_id] = types_inferred[node_value.id]

        elif isinstance(node_value, ast.Call):  # 这里可能是调用函数，或者构建对象。
            func = node_value.func
            if isinstance(func, ast.Name):
                func_name = func.id
                function_ret_value, function_defined = query_function_return_value_by_name(func_name)
                if function_defined:
                    types_inferred[target_id] = BoostTypeModel.from_type(function_ret_value)
                elif func_name in registered_types:
                    types_inferred[target_id] = registered_types[func_name]
                else:
                    raise ValueError(f"{node_value.__module__}:{node_value.lineno}函数或者类{func_name}未被注册")
            elif isinstance(func, ast.Attribute):
                chain = attribute.get_chain(func)
                chain.reverse()
                called = attribute.get_out_type_from_attribute_chain(chain, types_inferred)
                if type(called) == type:  # if it is a class variable, e.g., np.ndarray
                    types_inferred[target_id] = BoostTypeModel.from_type(called)
                elif called in function_types:
                    types_inferred[target_id] = BoostTypeModel.from_type(function_types[called])
                elif hasattr(called, '__annotations__') and "return" in called.__annotations__:
                    types_inferred[target_id] = BoostTypeModel.from_type(called.__annotations__['return'])
                else:
                    raise TypeError(f"[Line: {node_value.lineno}]Cannot infer return value of function {called}. "
                                    f"Please register this function or type the left variable.")
            elif isinstance(func, ast.Call):
                sub_call: ast.Call = func
                d = {}
                assign._infer_from_value('', sub_call, d)
                print(d)
                raise NotImplementedError
            else:
                raise NotImplementedError(ast.dump(node_value))

        elif isinstance(node_value, ast.BinOp):
            types_inferred[target_id] = BoostTypeModel.from_type(float)
            logger.warning(f'Found binop at {ast.dump(node_value)}. Assigning the left value to np.float')
            return

        elif isinstance(node_value, (ast.List, ast.Set, ast.Dict)):
            if isinstance(node_value, ast.List):
                types_inferred[target_id] = BoostTypeModel.from_type(list)
            elif isinstance(node_value, ast.Set):
                types_inferred[target_id] = BoostTypeModel.from_type(set)
            elif isinstance(node_value, ast.Dict):
                types_inferred[target_id] = BoostTypeModel.from_type(dict)
            else:
                raise NotImplementedError
        elif isinstance(node_value, ast.Compare):
            types_inferred[target_id] = BoostTypeModel.from_type(int)
        else:
            types_inferred[target_id] = BoostTypeModel.undetermined()

            logger.warning(f'ignored {ast.dump(node_value)}')
            print(f'ignored {ast.dump(node_value)}')
            # raise NotImplementedError(node_value.lineno)
            return

    @staticmethod
    def infer_from_value(target_id, node_value, types_inferred):
        assign._infer_from_value(target_id, node_value, types_inferred)
        return types_inferred


class attribute:
    @staticmethod
    def get_chain(attr: ast.Attribute):
        root_attr = copy.deepcopy(attr)
        attr_name_chain = []  # 名称链。意思是从右向左搜索方法的名称
        while isinstance(attr, ast.Attribute):
            attr_name_chain.append(attr.attr)
            attr = attr.value
        assert isinstance(attr,
                          ast.Name), f"Cannot parse chainned attribute expression '{astunparse.unparse(root_attr)}'," \
                                     f"You could write them in separated lines!"
        attr_name_chain.append(attr.id)
        return attr_name_chain

    @staticmethod
    def get_out_type_from_attribute_chain(chain: List[str], types_inferred: Dict[str, BoostTypeModel]):
        assert len(chain) > 1, chain
        if chain[0] in types_inferred:  # 寻找根对象。根对象可能是被注册的，或者已经被扫描过。
            value = types_inferred[chain[0]].root
        elif chain[0] in global_names:
            value = global_names[chain[0]]
        else:
            raise TypeError
        index = 1
        while index < len(chain):
            value = getattr(value, chain[index])
            index += 1
        return value


def register_type(cls_var: ClassVar,name=None):
    if name is None:
        name = cls_var.__name__
    registered_types[name] = BoostTypeModel.from_type(cls_var)
    print(cls_var.__name__)


def type_registered(t: type):
    for _, _t in registered_types.items():
        if issubclass(t, _t.root):
            return True
    return False


from Melodie import Agent, AgentList, Grid

registered_types: Dict[str, BoostTypeModel] = {  # 保留类型或者可以直接求值的类型
    k: BoostTypeModel.from_type(eval(k)) for k in ['int', 'str', 'bool', 'float', 'Agent', 'AgentList', 'Grid']
}
