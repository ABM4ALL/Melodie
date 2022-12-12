# -*- coding:utf-8 -*-
# @Time: 2022/11/23 21:42
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: excel.py
import os
from typing import List

from MelodieInfra.jsonobject import StringProperty, JsonObject, DefaultProperty, ObjectProperty
from .base import ExcelMeta


def path_validator(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(path)


class ExcelWriteRequest(JsonObject):
    path = StringProperty(
        required=True, validators=path_validator, name="path")
    data = DefaultProperty(required=True, name='data')
    sheet = StringProperty(required=True, name="sheet")


class ExcelReadSheetRequest(JsonObject):
    path = StringProperty(name="path",
                          required=True, validators=path_validator)
    sheet = StringProperty(name="sheet", required=False)


class ExcelReadSheetResponse(JsonObject):
    payload = DefaultProperty(name="payload", required=True)
    meta = ObjectProperty(ExcelMeta, name="meta", required=True)

    @staticmethod
    def create(payload, sheet: str, all_sheets: List[str]):
        return ExcelReadSheetResponse(
            payload=payload,
            meta=ExcelMeta({
                "currentSheet": sheet,
                "sheetNames": all_sheets,
                "widget": "table",
                "type": "excel"
            })
        )
