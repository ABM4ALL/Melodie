# -*- coding:utf-8 -*-
# @Time: 2022/12/13 22:32
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: model_static_inspector.py
import ast
import os
import sys
from typing import Dict, List, Optional, Type, TYPE_CHECKING, Union

import astunparse
import pprintast

if TYPE_CHECKING:
    from Melodie import Agent, DataCollector, Environment, Model


def get_model_ast(model: 'Type[Model]'):
    file = sys.modules[model.__module__].__file__
    with open(file, encoding='utf-8', errors='replace') as f:
        for node in ast.walk(ast.parse(f.read())):
            if isinstance(node, ast.ClassDef) and node.name == model.__name__:
                return node
    raise Exception('No classdef in such file!')


class ModelStructure:
    def __init__(self):
        self.agent_types: 'List[Type[Agent]]' = []
        self.environment_type: 'Optional[Type[Environment]]' = None
        self.data_collector_type: 'Optional[Type[DataCollector]]' = None

        self.env_structure: "Optional[ClassStructure]" = None
        self.agents_structure: "Optional[Dict[str, ClassStructure]]" = {}

    def add_agent_container_type(self, agent_container_ast: ast.Name):
        self.agent_types.append(agent_container_ast.id)

    def set_env_type(self, env_ast: ast.Name):
        self.environment_type = env_ast.id

    def set_data_collector_type(self, dc_ast: ast.Name):
        self.data_collector_type = dc_ast.id

    def __repr__(self):
        return f"<{self.__class__} {self.__dict__}>"


class EnvironmentStructure:
    def __init__(self):
        self.properties = []


class Attribute:
    def __init__(self, name, readonly: bool = False, attr_type=None):
        self.name: str = name
        self.readonly: bool = readonly
        self.type: str = attr_type

    def __repr__(self):
        return f"{self.name} <{'readonly ' if self.readonly else ''}property>"


class Function:
    def __init__(self, name: str):
        self.name = name


class ClassStructure:
    def __init__(self):
        self.name: str = ""
        self.bases = []
        self.attributes: Dict[str, Attribute] = {}
        self.methods: Dict[str, Function] = {}

    def __repr__(self):
        return f"<ClassStructure of class '{self.name}' extends {self.bases}, attributes: {self.attributes}," \
               f" methods: {self.methods} >"

    @staticmethod
    def from_cls_ast(cls_ast: ast.ClassDef) -> "ClassStructure":
        cls_structure = ClassStructure()
        cls_structure.name = cls_ast.name
        cls_structure.parse_inheritance(cls_ast)
        for node in ast.walk(cls_ast):
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                cls_structure.parse_assign(node)
            elif isinstance(node, (ast.FunctionDef)):
                cls_structure.parse_functiondef(node)
        print(cls_structure)
        return cls_structure

    def parse_inheritance(self, cls_ast: ast.ClassDef):
        for base in cls_ast.bases:
            self.bases.append(astunparse.unparse(base).strip())

    def parse_assign(self, node: Union[ast.Assign, ast.AnnAssign]):
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        for target in targets:
            if isinstance(target, ast.Attribute) and isinstance(target.value,
                                                                ast.Name) and target.value.id == 'self':
                self.attributes[target.attr] = Attribute(target.attr)

    def parse_functiondef(self, node: ast.FunctionDef):
        if len(node.decorator_list) > 0:
            for decorator_ast in node.decorator_list:
                if isinstance(decorator_ast, ast.Name) and decorator_ast.id == 'property':
                    if node.name not in self.attributes:
                        self.attributes[node.name] = Attribute(node.name, True)
                        return
                elif isinstance(decorator_ast, ast.Attribute) and decorator_ast.attr == 'setter' and isinstance(
                        decorator_ast.value, ast.Name):
                    attr_name = decorator_ast.value.id
                    if attr_name in self.attributes:
                        self.attributes[attr_name].readonly = False
                    else:
                        self.attributes[attr_name] = Attribute(node.name)
                    return
        self.methods[node.name] = Function(node.name)


def scan_attributes(cls_ast: ast.ClassDef) -> ClassStructure:
    """
    Scan attributes in a class

    :param cls_ast:
    :return:
    """
    return ClassStructure.from_cls_ast(cls_ast)


def find_class_in_files(cls_name: str, files_dir: str):
    print(files_dir)
    for root, dirs, files in os.walk(files_dir):
        for file in files:
            if file.endswith(".py"):
                file_abs_path = os.path.join(root, file)
                print(file_abs_path)
                with open(file_abs_path) as f:
                    tree: ast.Module = ast.parse(f.read())
                    for item in tree.body:
                        if isinstance(item, ast.ClassDef) and item.name == cls_name:
                            return item
    raise Exception("Class Not found!")


def walk_model_ast(model_ast: ast.ClassDef, file: str):
    model_structure = ModelStructure()
    functions = {'self.create_agent_list': lambda args: model_structure.add_agent_container_type(args[0]),
                 'self.create_environment': lambda args: model_structure.set_env_type(args[0]),
                 'self.create_data_collector': lambda args: model_structure.set_data_collector_type(args[0])}

    for node in ast.walk(model_ast):
        if isinstance(node, ast.Call):
            # print(astunparse.unparse(node.func))
            key = astunparse.unparse(node.func).strip()
            if key in functions:
                # print(functions)
                print(key, node.args)
                functions[key](node.args)
    # print(model_structure)

    for agent_type in model_structure.agent_types:
        agent_cls_ast = find_class_in_files(agent_type, os.path.dirname(file))
        model_structure.agents_structure[agent_type] = scan_attributes(agent_cls_ast)

    env_structure = scan_attributes(find_class_in_files(model_structure.environment_type, os.path.dirname(file)))
    model_structure.env_structure = env_structure
    # model_structure.agents_structure
