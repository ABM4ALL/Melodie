# -*- coding:utf-8 -*-
# @Time: 2022/12/13 21:50
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: ast_manipulator.py
import ast
import astunparse
from typing import Callable, List, Optional, Tuple


def load_func(file: str, func_name: str):
    with open(file, 'r', encoding='utf8', errors='replace') as f:
        root = ast.parse(f.read())
    for node in ast.walk(root):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            return root, node
    raise Exception(f"Function {func_name} not in {file}!")


class ASTManipulator:
    def __init__(self):
        self.ast: Optional[ast.AST] = None


class Function:
    def __init__(self, name: str):
        self.name = name


class FuncDefManipulator(ASTManipulator):
    # ast: ast.FunctionDef
    # root:
    def __init__(self, file: str, func_name: str):
        super().__init__()
        self.ast: ast.FunctionDef
        self.root: ast.Module
        self.root, self.ast = load_func(file, func_name)
        self.functions: List[Function] = [Function("self.add_agent_property")]

    @property
    def body(self) -> List[ast.stmt]:
        return self.ast.body

    # @property
    def get_records(self, func_name: str):
        records = []
        for node in ast.walk(self.ast):
            if self.is_valid_ast_node(func_name, node):
                records.append(self.parse_valid_node(node))
        return records

    def add_record(self, func_name: str, record: Tuple[str, str]):
        self.body.append(
            ast.Expr(
                value=ast.Call(
                    func=ast.parse(func_name),
                    args=[ast.Constant(value=s) for s in record],
                    keywords=[]
                )
            )
        )

    def remove_record(self, func_name: str, record: Tuple[str, str]):
        i = -1
        for i, item in enumerate(self.body):
            if isinstance(item, ast.Expr):
                node = item.value
                if self.is_valid_ast_node(func_name, node) and self.parse_valid_node(node) == record:
                    break
            else:
                continue

        if i >= 0:
            self.body.pop(i)

    @staticmethod
    def is_valid_ast_node(func_name: str, node: ast.AST):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            node = node.value
        if isinstance(node, (ast.Call,)):
            fname = astunparse.unparse(node.func).strip()
            if fname == func_name:
                return True

        return False

    def parse_valid_node(self, node: ast.Call):
        args = node.args
        value = []
        for arg in args:
            assert isinstance(arg, ast.Constant)
            value.append(arg.value)
        return tuple(value)
