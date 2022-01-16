# -*- coding:utf-8 -*-
# @Time: 2021/9/30 9:52
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: ast_parse.py

import ast
from typing import List

# path = '../../examples/Wealth-Distribution-New/WealthDistribution/api/agent.py'
# with open(path) as f:
#     res = ast.parse(f.read())


def find_class_defs(res)->List[ast.ClassDef]:
    classes = []
    for node in ast.walk(res):
        # if type()
        if type(node) == ast.ClassDef:
            classes.append(node)
    return classes
        # print(i,ast.FunctionDef, type(i))
    # return


def find_class_methods(class_ast: ast.ClassDef) -> List[ast.FunctionDef]:
    assert isinstance(class_ast, ast.ClassDef)
    functions = []

    for ast_node in ast.walk(class_ast):
        if type(ast_node) == ast.FunctionDef:
            functions.append(ast_node)
    return functions


def parse_setup_function(setup_function: ast.FunctionDef) -> List[str]:
    """
    Parse setup() method and get all properties defined there
    :param setup_function:
    :return:
    """
    function_body = setup_function.body
    names: List[str] = []
    for ast_node in function_body:
        if type(ast_node) == ast.Assign:
            assign_node: ast.Assign = ast_node
            for assign_target_node in assign_node.targets:
                if assign_target_node.__class__ == ast.Attribute:
                    attribute: ast.Attribute = assign_target_node
                    if attribute.value.__class__ == ast.Name and attribute.value.id == 'self':
                        property_name = attribute.attr
                        names.append(property_name)
    print(names)


# res = find_class_def(res)
# methods = find_class_methods(res)
# parse_setup_function(methods[0])
# print(methods)
# from pprintast import pprintast
#
# pprintast(res)
