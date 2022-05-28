# -*- coding:utf-8 -*-

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
