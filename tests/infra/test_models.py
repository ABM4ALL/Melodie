# -*- coding:utf-8 -*-
# @Time: 2022/11/23 22:18
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: test_file_io.py

from MelodieInfra import (
    ExcelReadSheetResponse,
    ExcelWriteRequest,
    assert_exc_type_occurs,
)


def test_excel_model():
    def f():
        r = ExcelWriteRequest({"path": "A:/", "sheet": "aaa", "data": []})
        print(r)

    assert_exc_type_occurs(FileNotFoundError, f)
    resp = ExcelReadSheetResponse(
        {
            "payload": [{}, {}],
            "meta": {
                "widget": "table",
                "type": "excel",
                "sheetNames": ["a", "b", "cc"],
                "currentSheet": "a",
            },
        }
    )
    print(resp.to_json())

    def f2():
        resp = ExcelReadSheetResponse(
            {
                "payload": [{}, {}],
                "meta": {
                    "widget": "table",
                    "type": "excel",
                    "sheetNames": {"a": "a"},
                    "currentSheet": "a",
                },
            }
        )
        print(resp.to_json())

    assert_exc_type_occurs(BaseException, f2)
