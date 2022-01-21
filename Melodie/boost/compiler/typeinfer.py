# -*- coding:utf-8 -*-
# @Time: 2021/10/21 10:38
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: typeinfer.py
import ast
import logging

import sys
from typing import List, Any, Dict, TypeVar, Union, Tuple, ClassVar

import astunparse
from pprintast import pprintast

from Melodie import Agent, AgentList

import numpy as np
from .typeinferlib import assign, registered_types, attribute, parse_annotation, BoostTypeModel

logging.basicConfig(level=logging.WARNING, stream=sys.stderr)
logger = logging.getLogger(__name__)


class TypeInferr(ast.NodeVisitor):
    def __init__(self, initial_types: Dict[str, Any], parsing_class_method=False):
        self.parsing_class_method = parsing_class_method
        self.types_inferred: Dict[str, BoostTypeModel] = initial_types.copy()
        for k in self.types_inferred.keys():
            assert isinstance(initial_types[k], BoostTypeModel)
        print(initial_types)

    def visit_FunctionDef(self, func_def: ast.FunctionDef) -> Any:
        argument: ast.arg = None
        for i, argument in enumerate(func_def.args.args):
            if i == 0 and self.parsing_class_method:
                continue
            if argument.arg not in self.types_inferred:
                if argument.annotation is None:
                    raise TypeError(
                        f"The annotation of argument {argument.arg} in function {func_def.name} is not defined")
                self.types_inferred[argument.arg] = parse_annotation(argument.annotation)
        if len(func_def.args.kw_defaults) != 0:  # kw args are not supported!
            raise NotImplementedError
        for body_node in func_def.body:
            self.visit(body_node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> Any:
        target = node.target
        if isinstance(target, ast.Name):
            self.types_inferred[target.id] = BoostTypeModel().from_annotation(node.annotation)
            return
        elif isinstance(target, ast.Attribute):
            self.types_inferred[astunparse.unparse(target).strip()] = BoostTypeModel().from_annotation(node.annotation)
            return
        else:
            raise NotImplementedError
        # self.types_inferred[target.id] = BoostTypeModel().from_annotation(node.annotation)
        # return

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
            assign.infer_from_value(astunparse.unparse(target).strip(), node.value, self.types_inferred)
            self.check_type(self.types_inferred)
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
        if isinstance(node.iter, ast.Name):
            if node.iter.id in self.types_inferred:
                if issubclass(self.types_inferred[node.iter.id].root, AgentList):
                    self.types_inferred[node.target.id] = BoostTypeModel.from_type(
                        self.types_inferred[node.iter.id].child_types()[0])
                    return
                elif issubclass(self.types_inferred[node.iter.id].root, np.ndarray):
                    self.types_inferred[node.target.id] = BoostTypeModel.from_type(np.ndarray)
                    return
                else:
                    raise NotImplementedError
            else:
                raise TypeError(f"node.iter was {ast.dump(node.iter)}, which has not been type-inferred.")
        elif isinstance(node.iter, ast.Call):
            func_name = node.iter.func.id
            if func_name == 'range':
                self.types_inferred[node.target.id] = BoostTypeModel.from_type(int)
                return
            else:

                raise NotImplementedError(ast.dump(node))
        else:
            raise ValueError(ast.dump(node))
        raise NotImplementedError(ast.dump(node))

    def check_type(self, inferred):
        for k in inferred.keys():

            assert isinstance(inferred[k], BoostTypeModel), (inferred[k], inferred)

    def __del__(self):
        self.check_type(self.types_inferred)
