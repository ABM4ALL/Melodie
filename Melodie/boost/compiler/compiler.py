# -*- coding:utf-8 -*-
# @Time: 2021/10/19 19:11
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: ast_parse.py

import ast
import inspect
import logging

import sys
from typing import List, Any, Dict, TypeVar, ClassVar

import astunparse
from pprintast import pprintast

from Melodie import Agent, AgentList
from Melodie.boost.compiler.typeinferlib import registered_types

from Melodie.network import Network
from Melodie.grid import Grid
from Melodie.management.ast_parse import find_class_defs, find_class_methods
import numpy as np

logging.basicConfig(level=logging.WARNING, stream=sys.stderr)
logger = logging.getLogger(__name__)
from Melodie.boost.compiler.typeinfer import TypeInferr
from .class_compiler import compile_to_jit_classes


class RewriteName(ast.NodeTransformer):
    def __init__(self, root_name: str, initial_types: Dict[str, TypeVar]):
        super().__init__()
        self.root_name = root_name

        self.types_inferred: Dict[str, TypeVar] = initial_types.copy()

    def visit_Name(self, node: ast.Name):
        if node.id == 'self':
            node.id = self.root_name
        return node


class RewriteCallEnv(ast.NodeTransformer):
    def __init__(self, root_name: str, initial_types: Dict[str, TypeVar]):
        super().__init__()
        self.root_name = root_name

        self.types_inferred: Dict[str, TypeVar] = initial_types.copy()

    # def visit_For(self, node: ast.For) -> Any:
    #
    #     self.visit(node.iter)
    #     return node

    def visit_Attribute(self, node: ast.Attribute) -> ast.Name:
        print(ast.dump(node))
        attribute_name = node.attr
        if isinstance(node.value, ast.Name):
            if node.value.id.startswith('___'):
                subs = ast.Subscript(value=node.value,
                                     slice=ast.Index(value=ast.Constant(value=attribute_name, kind=None)))
                return subs
            elif node.value.id in self.types_inferred:
                subs = ast.Subscript(value=node.value,
                                     slice=ast.Index(value=ast.Constant(value=attribute_name, kind=None)))
                return subs
            else:
                logger.warning(f"{ast.dump(node)}")
                return node
        return node

    def visit_Call(self, node: ast.Call) -> Any:
        if isinstance(node.func, ast.Attribute):
            attr: ast.Attribute = node.func
            while isinstance(attr.value, ast.Attribute):
                attr = attr.value
            assert isinstance(attr.value, ast.Name)
            if attr.value.id == self.root_name:
                name = ast.Name(id=self.root_name + "___" + attr.attr)
                node.func = name
                node.args.insert(0, ast.Name(id=self.root_name))
                return node
            elif attr.value.id in self.types_inferred:  # 如果调用的是agent的方法，则传入的第一个参数为agent
                type_var = self.types_inferred[attr.value.id]
                if issubclass(type_var, Agent):
                    node.func = ast.Name(id='___agent___' + attr.attr, )
                    node.args.insert(0, ast.Name(id=attr.value.id))
                    return node
                elif issubclass(type_var, AgentList):
                    node.func = ast.Name(id='___agent___manager___' + attr.attr)
                    node.args.insert(0, ast.Name(id=attr.value.id))
                    return node
                elif issubclass(type_var, (Network, Grid)):  # Network已经会传入jitclass.
                    return node
                else:
                    raise TypeError(ast.dump(node.func))
            else:
                logger.warning(f"Skipping the unrecognized function:{ast.dump(attr)}")
                return node
        logger.warning(f"Skipping unexpected function:{node}")
        return node


class RewriteCallModel(ast.NodeTransformer):
    def __init__(self, root_name: str, initial_types: Dict[str, TypeVar], sub_components=None):
        super().__init__()
        self.root_name = root_name

        self.types_inferred: Dict[str, TypeVar] = initial_types.copy()

        self.sub_components = {"environment"}

        if sub_components is not None:
            assert isinstance(sub_components, set)
            self.sub_components.update(sub_components)

    def visit_Attribute(self, node: ast.Attribute) -> ast.Name:
        print(ast.dump(node))
        attr: ast.Attribute = node
        attr_name_chain = [attr.attr]  # 名称链。意思是从右向左搜索方法的名称
        while isinstance(attr.value, ast.Attribute):
            attr = attr.value
            attr_name_chain.append(attr.attr)
        # print(attr_name_chain)
        assert isinstance(attr.value, ast.Name)
        # if attr.value.id.startswith(self.root_name):
        #     # print(attr.value.id)
        #     pass
        # raise NotImplementedError
        node.value = self.visit(node.value)
        return node
        # print(ast.dump(node))
        # attribute_name = node.attr
        # if isinstance(node.value, ast.Name):
        #     if node.value.id.startswith('___'):
        #         subs = ast.Subscript(value=node.value,
        #                              slice=ast.Index(value=ast.Constant(value=attribute_name, kind=None)))
        #         return subs
        #     elif node.value.id in self.types_inferred:
        #         subs = ast.Subscript(value=node.value,
        #                              slice=ast.Index(value=ast.Constant(value=attribute_name, kind=None)))
        #         return subs
        #     else:
        #         logger.warning(f"{ast.dump(node)}")
        #         return node
        # else:
        #     raise NotImplementedError
        # return node

    def visit_Call(self, node: ast.Call) -> Any:
        # print(ast.dump(node))
        if isinstance(node.func, ast.Attribute):
            attr: ast.Attribute = node.func
            attr_name_chain = [attr.attr]  # 名称链。意思是从右向左搜索方法的名称
            while isinstance(attr.value, ast.Attribute):
                attr = attr.value
                attr_name_chain.append(attr.attr)
            assert isinstance(attr.value, ast.Name)
            if attr.value.id == self.root_name:
                if attr_name_chain[-1] in self.sub_components:  # 调用了agent_manager或者environment等
                    name = ast.Name(id=f"___{attr_name_chain[-1]}___" + attr_name_chain[0])
                    node.func = name
                    # return node
                    node.args.insert(0, ast.Name(id="___model." + attr_name_chain[-1]))
                    # raise NotImplementedError
                else:
                    logger.warning(f"Ignored model `self.` call: {attr_name_chain}")
                    pass
                    # raise NotImplementedError
            else:
                logger.warning(f"Ignored call: {ast.dump(node)} at line {node.lineno}")

            # if attr.value.id == self.root_name:
            #     name = ast.Name(id=self.root_name + "___" + attr.attr)
            #     node.func = name
            #     node.args.insert(0, ast.Name(id=self.root_name))
            #     return node
            # elif attr.value.id in self.types_inferred:  # 如果调用的是agent的方法，则传入的第一个参数为agent
            #     type_var = self.types_inferred[attr.value.id]
            #     if issubclass(type_var, Agent):
            #         node.func = ast.Name(id='___agent___' + attr.attr, )
            #         node.args.insert(0, ast.Name(id=attr.value.id))
            #         return node
            #     elif issubclass(type_var, AgentList):
            #         node.func = ast.Name(id='___agent___manager___' + attr.attr)
            #         node.args.insert(0, ast.Name(id=attr.value.id))
            #         return node
            #     else:
            #         raise TypeError(ast.dump(node.func))
            # else:
            #     logger.warning(f"Skipping the unrecognized function:{ast.dump(attr)}")
            #     return node
        logger.warning(f"Skipping unexpected function:{ast.dump(node)}")

        node.func = self.visit(node.func)
        args = node.args
        new_args = []
        for i, arg in enumerate(args):
            new_args.append(self.visit(arg))
        node.args = new_args
        return node


def get_all_self_attrs(method_ast) -> List[str]:
    attr_names = []
    for node in ast.walk(method_ast):
        if isinstance(node, ast.Name):
            if node.id.startswith('___'):
                attr_names.append(node.id)
    return attr_names


class GINIAgent(Agent):
    pass


prefix = """
import time
import random
import numpy as np
from Melodie.boost.compiler.boostlib import ___agent___manager___random_sample
import numba

"""


def try_eval_type(s):
    try:
        return eval(s)
    except:
        import traceback
        traceback.print_exc()
        return None


def modify_ast_environment(method: ast.FunctionDef, root_name: str):
    annotations = {}
    for i, arg in enumerate(method.args.args):

        annotations[arg.arg] = arg.annotation
        if i > 0:
            assert arg.annotation is not None
            annotation = arg.annotation
            if isinstance(annotation, ast.Constant):
                annotations[arg.arg] = eval(arg.annotation.value)
            elif isinstance(annotation, ast.Name):
                annotations[arg.arg] = eval(annotation.id)
    RewriteName(root_name, {}).visit(method)

    ti = TypeInferr(annotations)
    ti.visit(method)

    print('types inferred:', ti.types_inferred)
    pprintast(method)
    rce = RewriteCallEnv(root_name, ti.types_inferred)
    rce.visit(method)
    method.args.args[0].arg = root_name
    method.name = root_name + '___' + method.name

    print('+++++++++++++++++++++++++++++++++')
    # print(pprintast(method))
    r = astunparse.unparse(method)

    r = '@numba.jit\n' + r.lstrip() + "\n\n"
    return r


def modify_ast_model(method, root_name, model_components):
    annotations = {}
    for i, arg in enumerate(method.args.args):

        annotations[arg.arg] = arg.annotation
        if i > 0:
            assert arg.annotation is not None
            if arg.annotation.value in registered_types:
                annotations[arg.arg] = registered_types[arg.annotation.value]
            else:
                annotations[arg.arg] = eval(arg.annotation.value)

    RewriteName(root_name, {}).visit(method)

    ti = TypeInferr(annotations)
    ti.visit(method)

    print('types inferred:', ti.types_inferred)
    pprintast(method)
    rce = RewriteCallModel(root_name, ti.types_inferred, sub_components=model_components)
    rce.visit(method)
    method.args.args[0].arg = root_name
    method.name = root_name + '___' + method.name

    print('+++++++++++++++++++++++++++++++++')
    print(pprintast(method))
    r = astunparse.unparse(method)

    return r


def get_class_in_file(filename: str, cls_name) -> ast.ClassDef:
    with open(filename, encoding="utf8") as f:
        root = ast.parse(f.read())
        for node in ast.walk(root):
            if isinstance(node, ast.ClassDef) and node.name == cls_name:
                return node
    raise ValueError


def get_ast(agent_class: ClassVar, environment_class, model_class):
    agent_file = inspect.getfile(agent_class)
    env_file = inspect.getfile(environment_class)
    model_file = inspect.getfile(model_class)
    return (get_class_in_file(agent_file, agent_class.__name__),
            get_class_in_file(env_file, environment_class.__name__),
            get_class_in_file(model_file, model_class.__name__))


def conv(agent_class, environment_class, model_class, output, model_components=None):
    agent_class, env_class, model_class = get_ast(agent_class, environment_class, model_class)
    f = open(output, 'w')
    f.write(prefix)

    f.write(compile_to_jit_classes())

    for method in find_class_methods(agent_class):
        if method.name not in {'setup', 'post_setup'}:
            code = modify_ast_environment(method, '___agent')
            f.write(code)

    for method in find_class_methods(env_class):
        if method.name != 'setup':
            code = modify_ast_environment(method, '___environment')
            print(code)
            f.write(code)

    for method in find_class_methods(model_class):
        if method.name != 'setup':
            code = modify_ast_model(method, '___model', model_components)
            print(code)
            f.write(code)

    f.close()


if __name__ == '__main__':
    conv('src/ast_demo.py', 'out.py')
