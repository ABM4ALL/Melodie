# -*- coding:utf-8 -*-
# @Time: 2021/12/15 10:08
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: property_parser.py
import ast
import code
from typing import Union, TYPE_CHECKING, Type, ClassVar, Dict, Tuple, List

from Melodie.boost.compiler.typeinfer import TypeInferr
from Melodie.management.ast_parse import find_class_methods
from Melodie import Agent, AgentList, Environment
from Melodie.boost.compiler.typeinferlib import BoostTypeModel
# if TYPE_CHECKING:




def parse_component_properties(cls: ast.ClassDef) -> Dict:
    assert isinstance(cls, ast.ClassDef)
    inferred = {}
    for method in find_class_methods(cls):
        if method.name == 'setup':
            inferr = TypeInferr({}, True)
            inferr.visit(method)
            inferred.update({k.split('.')[1]: v for k, v in inferr.types_inferred.items() if k.startswith('self.')})
            return inferred
    raise ValueError(f"No setup method in class {cls}")


def gen_dtypes(inferred_dtypes: Dict[str, "BoostTypeModel"]) -> List[Tuple[str, str]]:
    dtypes: List[Tuple[str, str]] = []
    user_defined_spot_attr_names: List[str] = []
    for attr_name, btm in inferred_dtypes.items():
        user_defined_spot_attr_names.append(attr_name)
        if issubclass(btm.root, (int, bool)):
            dtypes.append((attr_name, 'i8'))
        elif issubclass(btm.root, float):
            dtypes.append((attr_name, 'f8'))
        else:
            raise ValueError(f'Unsupported Spot attribute "{attr_name}" with BoostTypeModel {btm} ')
    return dtypes


def generate_array(cls: "Union[ClassVar[Agent], ClassVar[Environment]]", cls_ast, length=0) -> str:
    """

    :param cls:
    :param cls_ast:
    :param length: 如果为0，则生成0*1；否则生成length长度的Array
    :return:
    """

    dtypes = gen_dtypes(parse_component_properties(cls_ast))
    if issubclass(cls, Agent):
        return f"""_{cls.__name__}_ARRAY = np.zeros(({length},), dtype={dtypes})"""
    elif issubclass(cls, Environment):
        return f"""_{cls.__name__}_ARRAY = np.zeros(1, dtype={dtypes})"""
    else:
        raise NotImplementedError
