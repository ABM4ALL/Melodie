# -*- coding:utf-8 -*-
# @Time: 2022/11/23 21:33
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: database.py

from MelodieInfra.jsonobject import JsonObject, StringProperty

class DatabaseBasicRequest(JsonObject):
    connection_string = StringProperty(name="connectionString", required=True)

class DatabaseQueryRequest(DatabaseBasicRequest):
    sql = StringProperty(name="sql", required=True)

