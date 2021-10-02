# -*- coding:utf-8 -*-
# @Time: 2021/9/30 10:33
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: ast_unparse.py
import ast
from typing import List

import astunparse
from pprintast import pprintast


def chain_property(method: str) -> ast.Attribute:
    chain: List[str] = method.split('.')
    attr = None
    root_name = chain[0]
    for attr_name in chain[1:]:
        if attr is None:
            attr = ast.Attribute(
                value=ast.Name(id=root_name),
                attr=attr_name,
                # 由于只需要生成代码，因此不用声明Load或者Store
            )
        else:
            attr = ast.Attribute(
                value=attr,
                attr=attr_name
            )
    pprintast(attr)
    return attr


# print(generate_chain_property_getter('np.random.uniform'))

setup = ast.FunctionDef(name='setup',
                        args=ast.arguments(
                            posonlyargs=[],
                            args=[
                                ast.arg(arg='self', annotation=None, type_comment=None)
                            ],
                            vararg=None,
                            kwonlyargs=[],
                            kw_defaults=[],
                            kwarg=None,
                            defaults=[]),
                        body=[
                            ast.Assign(
                                targets=[
                                    chain_property('self.id')
                                    # ast.Attribute(
                                    #     value=ast.Name(id='self', ctx=ast.Load()),
                                    #     attr='id',
                                    #     ctx=ast.Store())
                                ],
                                value=ast.Constant(value=0, kind=None),
                                type_comment=None),
                            ast.Assign(
                                targets=[
                                    ast.Name(id='rand', ctx=ast.Store()),
                                ],
                                value=ast.Call(
                                    func=chain_property('np.random123.uniform'),
                                    args=[
                                        ast.Constant(value=0, kind=None),
                                        ast.Constant(value=1, kind=None),
                                    ],
                                    keywords=[]), type_comment=None),
                        ],
                        decorator_list=[],
                        returns=None,
                        type_comment=None
                        )
cls = ast.ClassDef(name='GINIAgent', bases=[ast.Name(id='Agent', ctx=ast.Load())],
                   keywords=[], body=[
        setup
    ], decorator_list=[])
print(astunparse.unparse(cls))
print(astunparse.unparse(
    ast.Assign(
        targets=[chain_property('self.id')],
        value=ast.Constant(value=0, kind=None)))
)
