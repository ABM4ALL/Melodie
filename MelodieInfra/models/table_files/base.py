# -*- coding:utf-8 -*-
# @Time: 2022/11/24 17:59
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: base.py.py
from ...jsonobject import JsonObject, StringProperty, ListProperty


def assert_is_list(obj):
    assert isinstance(obj, list)


class ExcelMeta(JsonObject):
    widget = StringProperty(name="widget")
    type = StringProperty(name="type")
    sheet_names = ListProperty(str, name="sheetNames", validators=assert_is_list)
    current_sheet = StringProperty(name='currentSheet')
