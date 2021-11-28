# -*- coding:utf-8 -*-
# @Time: 2021/10/21 10:38
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: typeinfer.py
import ast
import logging

import sys
from typing import List, Any, Dict, TypeVar, Union, Tuple, ClassVar

from Melodie import Agent, AgentList

import numpy as np
from .typeinferlib import assign, registered_types, attribute, ArrayOfAgents

logging.basicConfig(level=logging.WARNING, stream=sys.stderr)
logger = logging.getLogger(__name__)


def parse_annotation_type(anno: Union[ast.Name]):
    if isinstance(anno, ast.Name):
        if anno.id in registered_types:
            return registered_types[anno.id]
        else:
            raise NotImplementedError
    elif type(anno) == ast.Constant:
        return eval(anno.value)
    elif anno is None:
        raise TypeError("Do not use `None` as the type annotation!")
    else:
        raise NotImplementedError(anno)


class TypeInferr(ast.NodeVisitor):
    def __init__(self, initial_types: Dict[str, Any]):
        self.types_inferred: Dict[str, Any] = initial_types.copy()

    def visit_FunctionDef(self, func_def: ast.FunctionDef) -> Any:
        argument: ast.arg = None
        for argument in func_def.args.args:
            if argument.arg not in self.types_inferred:
                self.types_inferred[argument.arg] = parse_annotation_type(argument.annotation)
        if len(func_def.args.kw_defaults) != 0:  # kw args are not supported!
            raise NotImplementedError
        for body_node in func_def.body:
            self.visit(body_node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> Any:
        target = node.target
        assert isinstance(target, ast.Name), "Assert could only be to a single variable"
        if isinstance(node.value, ast.Constant):
            if node.value.value is None:
                assert isinstance(node.annotation, ast.Constant)
                self.types_inferred[target.id] = eval(node.annotation.value)
                # raise NotImplementedError
            else:
                raise TypeError(f"Annotation {node.annotation.value} does not match {node.value.value}!")
                # self.types_inferred[target.id] = type(node.value.value)
        elif isinstance(node.annotation, ast.Name):
            if node.annotation.id in registered_types:  #
                self.types_inferred[target.id] = registered_types[node.annotation.id]
            else:
                raise NotImplementedError
        else:
            logger.warning(f"skipping annassign {ast.dump(node)}")
            print(f"skipping annassign {ast.dump(node)}")
            assert isinstance(node.annotation, ast.Constant)
            if node.annotation.value in registered_types:
                annotated_type = registered_types[node.annotation.value]
            else:
                annotated_type = eval(node.annotation.value)
            if target.id in self.types_inferred:
                inferred_type = self.types_inferred[target.id]
                assert issubclass(annotated_type, inferred_type)
            else:
                self.types_inferred[target.id] = annotated_type

    def visit_Assign(self, node: ast.Assign) -> Any:
        assert len(node.targets) == 1
        target = node.targets[0]
        if isinstance(target, ast.Name):
            assign.infer_from_value(target.id, node.value, self.types_inferred)
            return
        elif isinstance(target, ast.Tuple):
            names = target.elts
            for name in names:
                if name.id not in self.types_inferred:
                    raise TypeError(f'Vars in Tuple assigning should be annotated declared '
                                    f'before.')
            return
        elif isinstance(target, ast.Attribute):
            logger.warning(f'Skipping the assigning to attribute {ast.dump(target)}')
            return
        elif isinstance(target, ast.Subscript):
            logger.warning(f'Skipping the assigning to subscript {ast.dump(target)}')
            return
        else:
            raise NotImplementedError(ast.dump(target))

    def visit_For(self, node: ast.For) -> Any:
        self._visit_For(node)
        for child in node.body:
            self.visit(child)

    def _visit_For(self, node: ast.For) -> Any:

        assert isinstance(node.target, ast.Name), "当前只支持ast.Name型作为for循环的迭代变量"
        if isinstance(node.iter, ast.Name):  # "当前只支持ast.Name型作为for循环的迭代变量"
            if node.iter.id in self.types_inferred:
                if issubclass(self.types_inferred[node.iter.id], AgentList):
                    self.types_inferred[node.target.id] = Agent
                    return
                elif issubclass(self.types_inferred[node.iter.id], np.ndarray):
                    self.types_inferred[node.target.id] = np.ndarray
                    return
                else:
                    raise NotImplementedError
            else:
                raise TypeError(f"node.iter was {ast.dump(node.iter)}, which has not been type-inferred.")
        elif isinstance(node.iter, ast.Call):
            func_name = node.iter.func.id
            if func_name == 'range':
                self.types_inferred[node.target.id] = int
                return
            else:

                raise NotImplementedError(ast.dump(node))
        else:
            raise ValueError(ast.dump(node))
        # pprintast(node)/
        raise NotImplementedError(ast.dump(node))
        # return node
