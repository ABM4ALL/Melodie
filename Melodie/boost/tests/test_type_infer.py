# -*- coding:utf-8 -*-
# @Time: 2021/10/21 10:40
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: test_type_infer.py
import ast
import os.path
from typing import Dict

from pprintast import pprintast

from Melodie.boost.compiler.typeinfer import TypeInferr
from data.classes import ClsTest
# from Melodie.management.ast_parse import f

root = os.path.dirname(__file__)
data_folder = os.path.join(root, 'data')


def get_function(filename, funcname) -> ast.FunctionDef:
    with open(os.path.join(data_folder, filename)) as f:
        root = ast.parse(f.read())
    for node in ast.walk(root):
        if isinstance(node, ast.FunctionDef):
            if node.name == funcname:
                return node
    raise ValueError(f"function {funcname} not found in file {filename}")


def get_inferred_types(filename, funcname, inferred=None) -> Dict:
    f = get_function(filename, funcname)
    pprintast(f)
    inferer = TypeInferr({} if inferred is None else inferred)
    inferer.visit(f)
    return inferer.types_inferred


def test_type_infer():
    defs = get_inferred_types("basics.py", 'constant_types_in_if')
    assert defs['a'] == int
    assert defs['b'] == float
    assert defs['c'] == bool
    assert defs['d'] == str
    assert defs['e'] == type(None)
    defs = get_inferred_types("basics.py", 'constant_types_in_for_loop')
    assert defs['a'] == int
    assert defs['b'] == float
    assert defs['c'] == bool
    assert defs['d'] == str
    assert defs['e'] == type(None)


def test_infer_containers():
    defs = get_inferred_types("basics.py", 'constant_types_with_args')
    assert defs['a'] == int
    assert defs['b'] == float
    assert defs['c'] == bool
    assert defs['d'] == str
    print(defs)


def test_const_with_args():
    defs = get_inferred_types("basics.py", 'constant_types_with_args')
    assert defs['a'] == int
    assert defs['b'] == float
    assert defs['c'] == bool
    assert defs['d'] == str
    print(defs)


def test_container_types():
    defs = get_inferred_types("basics.py", 'container_types')
    assert defs['l'] == list
    assert defs['m'] == dict
    assert defs['s'] == set


def test_assign():
    defs = get_inferred_types("basics.py", 'assigning')
    assert defs['x'] == set
    print(defs)


def test_property_access():
    ClsTest.b = 0
    print(ClsTest.__dict__)
    defs = get_inferred_types("classes.py", 'property_access', {"self": ClsTest})
    # assert defs['x'] == set
    print(defs)

def test_money_transfer():
    ClsTest.b = 0
    print(ClsTest.__dict__)
    defs = get_inferred_types("classes.py", 'go_money_transfer', {"self": ClsTest})
    # assert defs['x'] == set
    print(defs)
