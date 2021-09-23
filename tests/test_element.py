# -*- coding:utf-8 -*-
# @Time: 2021/9/23 16:03
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: test_element.py

from Melodie.element import Element


def test_element():
    elem = Element()
    elem.a = 123
    elem.set_params({'a': 456})
    assert elem.a == 456
    try:
        elem.set_params({'b': 567})
    except Exception as e:
        print(e)
