# -*- coding:utf-8 -*-
# @Time: 2022/11/23 21:33
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: database.py

from typing import List
from MelodieInfra.jsonobject import JsonObject, StringProperty, BooleanProperty, ListProperty, IntegerProperty


class DatabaseBasicRequest(JsonObject):
    connection_string = StringProperty(name="connectionString", required=True)


class DatabaseQueryRequest(DatabaseBasicRequest):
    sql = StringProperty(name="sql", required=True)

class ColumnSchema(JsonObject):
    name = StringProperty()
    type = StringProperty(validators=[lambda t : t in {'int', "float", 'str', 'bool'}])
    label = StringProperty()
    readonly = BooleanProperty(default=False)
    width = IntegerProperty(default=0)

class ColumnSchemas(JsonObject):
    table_name: str = StringProperty()
    table_label: str = StringProperty()
    columns: List[ColumnSchema] = ListProperty(ColumnSchema)

    def label_to_name(self, label: str):
        for schema in self.columns:
            if schema.label==label:
                return schema.name
        raise KeyError(f"Schema label not defined: {label}")