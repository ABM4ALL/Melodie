# -*- coding:utf-8 -*-
# @Time: 2021/12/13 14:07
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: class_compiler.py
import ast
import inspect
from typing import Dict, ClassVar, Any, Tuple

import astunparse
from pprintast import pprintast

from .typeinfer import TypeInferr
from .typeinferlib import registered_types, BoostTypeModel
from ... import AgentList
from ...management.ast_parse import find_class_methods

_expected_to_compile_classes = {

}

dtype_map = {
    int: "numba.int64",
    float: "numba.float64",
    bool: "numba.boolean",
    str: "numba.unicode",
}


def add_dtype_map(cls, s):
    dtype_map[cls] = s


def add_custom_jit_class(cls: ClassVar[Any]):
    _expected_to_compile_classes[cls.__name__] = cls


def generate_jitclass_annotation(types: Dict[str, BoostTypeModel]):
    s = "@jitclass(["
    for k, btm in types.items():
        if btm.root in dtype_map.keys():
            s += f"('{k}', {dtype_map[btm.root]}),"
        elif btm.root == AgentList:
            s += f"('{k}', numba.typeof(_{btm.child_types()[0].__name__}_ARRAY)), "
        else:
            raise NotImplementedError
    s += "])"
    return s


def compile_general_class(cls: ClassVar[Any]) -> str:
    from .compiler import get_class_in_file
    current_cls = cls
    cls_ast: ast.ClassDef = None
    cls_ast_list = []
    # 寻找当前类及其基类，暂时不允许多继承。
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
            current_cls = registered_types[base_cls_id].root
    print(cls_ast_list)

    inferred = {}
    cls_ast_list.reverse()
    _init_method_defined = False
    cls_strs: Dict[str, Tuple[int, str]] = {}
    # 从基类开始往下找，扫描__init__方法里面的内容。
    for i, cls_ast in enumerate(cls_ast_list):
        for method in find_class_methods(cls_ast):
            if method.name == '__init__':
                _init_method_defined = True
                inferr = TypeInferr({}, True)
                inferr.visit(method)
                inferred.update({k.split('.')[1]: v for k, v in inferr.types_inferred.items() if k.startswith('self.')})
                break
        string = ""
        if cls_ast.name == cls.__name__:
            string += generate_jitclass_annotation(inferred) + "\n"
        string += astunparse.unparse(cls_ast).strip() + "\n"
        cls_strs[cls_ast.name] = (i, string)
        # print(astunparse.unparse(cls_ast))
    assert _init_method_defined, f"No '__init__' method defined for custom class {cls}."
    print(string)
    return cls_strs


def compile_to_jit_classes() -> str:
    s = ''
    classes: Dict[str, Tuple[int, str]] = {}
    for name, cls in _expected_to_compile_classes.items():
        compiled = compile_general_class(cls)
        classes.update(compiled)
    layer = 0
    print("aaaaa", classes)
    while len(classes) > 0:
        keys = list(classes.keys())
        for k in keys:
            if classes[k][0] == layer:
                s += classes.pop(k)[1]
        layer += 1
    return s
