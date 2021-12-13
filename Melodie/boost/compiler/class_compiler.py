# -*- coding:utf-8 -*-
# @Time: 2021/12/13 14:07
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: class_compiler.py
import ast
import inspect
from typing import Dict, ClassVar, Any

import astunparse
from pprintast import pprintast

from .typeinfer import TypeInferr
from .typeinferlib import registered_types
from ...management.ast_parse import find_class_methods

_expected_to_compile_classes = {

}

dtype_map = {
    int: "numba.int64",
    float: "numba.float64",
    bool: "numba.boolean",
    str: "numba.unicode"

}


def add_jit_class(cls: ClassVar[Any]):
    _expected_to_compile_classes[cls.__name__] = cls


def generate_jitclass_annotation(types):
    s = "@jitclass(["
    for k, dtype in types.items():
        s += f"({k}, {dtype_map[dtype]}),"
    s += "])"
    return s


def compile_general_class(cls: ClassVar[Any]) -> str:
    from .compiler import get_class_in_file
    current_cls = cls
    cls_ast: ast.ClassDef = None
    cls_ast_list = []
    while cls_ast is None or len(cls_ast.bases) > 0:
        file = inspect.getfile(current_cls)
        cls_ast: ast.ClassDef = get_class_in_file(file, current_cls.__name__)
        print(pprintast(cls_ast))
        cls_ast_list.append(cls_ast)
        assert isinstance(cls_ast, ast.ClassDef)
        assert len(cls_ast.bases) in {0, 1}
        if len(cls_ast.bases) > 0:
            base_cls_name: ast.Name = cls_ast.bases[0]
            base_cls_id = base_cls_name.id
            print(base_cls_id)
            current_cls = registered_types[base_cls_id]
    print(cls_ast_list)
    string = ""
    inferred = {}
    cls_ast_list.reverse()
    for i, cls_ast in enumerate(cls_ast_list):
        for method in find_class_methods(cls_ast):
            if method.name == '__init__':
                inferr = TypeInferr({}, True)
                inferr.visit(method)
                inferred.update({k.split('.')[1]: v for k, v in inferr.types_inferred.items()})
                break
        if cls_ast.name == cls.__name__:
            string += generate_jitclass_annotation(inferred) + "\n"
        string += astunparse.unparse(cls_ast).strip() + "\n"
        # print(astunparse.unparse(cls_ast))
    print(string)
    return string


def compile_to_jit_classes() -> str:
    s = ''
    for name, cls in _expected_to_compile_classes.items():
        s += compile_general_class(cls)
    return s
