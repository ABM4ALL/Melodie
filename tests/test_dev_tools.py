# -*- coding:utf-8 -*-
# @Time: 2021/10/8 13:52
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: test_dev_tools.py
import os.path
import sys
import platform
import warnings

from Melodie.management.manager_server import get_mermaid


def test_get_mermaid():
    x, y, z = platform.python_version_tuple()
    if not int(y) == 8:
        warnings.warn('Warning, control flow analysis only stable on python 3.8!')
        return
    mermaid = get_mermaid(os.path.join(os.path.dirname(__file__), 'resources', 'demos', 'astdemo.py'), 'demofunction')
    print(mermaid)
    mermaid = get_mermaid(os.path.join(os.path.dirname(__file__), 'resources', 'demos', 'astdemo.py'), 'demofunction2')
    print(mermaid)

    mermaid = get_mermaid(
        os.path.join(
            os.path.dirname(__file__),
            'resources',
            'demos',
            'astdemo.py'),
        'test_tuple_parse')

    mermaid = get_mermaid(
        os.path.join(
            os.path.dirname(__file__),
            'resources',
            'demos',
            'astdemo.py'),
        'test_enclosures')
    print(mermaid)

    mermaid = get_mermaid(
        os.path.join(
            os.path.dirname(__file__),
            'resources',
            'demos',
            'astdemo.py'),
        'test_loops')
    print(mermaid)
