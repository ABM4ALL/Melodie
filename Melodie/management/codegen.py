# -*- coding:utf-8 -*-
# @Time: 2021/9/30 11:18
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: codegen.py

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


nodes = [{
    'type': 'block',
    'code': 'a+=1',
    'id': 0,
    'next': 1
}, {
    'id': 1,
    'type': 'condition',
    'condition': 'a==1',
    'true': 0,
    'false': 1
}
]

unparsed = astunparse.unparse([
    ast.Assign(
        targets=[chain_property('self.id')],
        value=ast.Constant(value=0, kind=None))
])
print(unparsed)
