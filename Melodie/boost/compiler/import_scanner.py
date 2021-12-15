# -*- coding:utf-8 -*-
# @Time: 2021/12/14 16:33
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: import_scanner.py
import ast
import copy
from typing import List, Union

import astunparse

# 被扫描的所有文件中，用于import的语句。
all_import_statements: List[Union[ast.Import, ast.ImportFrom]] = []


def scan_imports(file: str):
    """
    扫描某一个文件的导入语句，将结果存储到all_import_statements中。
    :param file:
    :return:
    """
    global all_import_statements
    with open(file) as f:
        file_ast = ast.parse(f.read())
    import_statements: List[Union[ast.Import, ast.ImportFrom]] = []
    for node in ast.walk(file_ast):
        if isinstance(node, ast.Import):
            import_statements.append(node)
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0:
                import_statements.append(node)
        else:
            pass
    import_statements = copy.deepcopy(import_statements)
    all_import_statements += import_statements
    return import_statements


def import_statements_to_str() -> str:
    statements: List[str] = []
    for import_statement in all_import_statements:
        statements.append(astunparse.unparse(import_statement).strip())
    statements = list(set(statements))
    return "\n".join(statements) + "\n"
