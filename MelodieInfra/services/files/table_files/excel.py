# -*- coding:utf-8 -*-
# @Time: 2022/11/23 21:56
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: excel.py
import json
import os
import tempfile
from typing import Any, List, cast

import openpyxl
import pandas as pd

from MelodieInfra.models import ExcelWriteRequest, DataServiceStatus, ExcelReadSheetRequest, ExcelReadSheetResponse, \
    DataServiceState


def df_to_json(df: pd.DataFrame):
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        df.to_json(tf.name, orient="table", indent=4, index=False)
        data = tf.read()
        tf.close()
    data = json.loads(data)
    for item in data["schema"]["fields"]:
        if item["type"] == "integer":
            item["type"] = "number"
    return data


class ExcelManipulator:
    def __init__(self, filename: str) -> None:
        self.filename = filename

    def get_sheet_names(self):
        return pd.ExcelFile(self.filename).sheet_names

    def read_sheet(self, sheet_name: str = None, **kwargs):
        return pd.read_excel(self.filename, sheet_name, **kwargs)

    def write_to_sheet(self, df: pd.DataFrame, sheet_name: str, **kwargs):
        book = None
        sheet_exist = False
        if os.path.exists(self.filename):
            book = openpyxl.load_workbook(self.filename)
            sheet_exist = sheet_name in self.get_sheet_names()
        if sheet_exist:
            with pd.ExcelWriter(
                    self.filename, engine="openpyxl", mode="a", if_sheet_exists="replace"
            ) as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        else:
            writer = pd.ExcelWriter(self.filename, engine="openpyxl")
            print(sheet_exist)
            if book is not None:
                writer.book = book
            df.to_excel(writer, sheet_name, index=False)
            writer.save()


class ExcelDataService:
    @staticmethod
    def write_excel(req: ExcelWriteRequest) -> DataServiceStatus:
        """
        Write data to excel file.

        :param req:
        :return: error message, None means success.
        """
        _, ext = os.path.splitext(req.path)
        ext = ext[1:]
        if ext in {"xls", "xlsx"}:
            df = pd.DataFrame(req.data)
            try:
                if req.sheet is not None:
                    em = ExcelManipulator(req.path)
                    em.write_to_sheet(df, req.sheet)
                else:
                    df.to_excel(req.path, index=False)
                return DataServiceStatus(status=DataServiceState.SUCCESS, msg='Succeeded saved table file!')
            except BaseException as e:
                return DataServiceStatus(status=DataServiceState.ERROR, msg=f"{e}")
        else:
            return DataServiceStatus(status=DataServiceState.ERROR,
                                     msg=f"Extension name {ext} unsupported for excel files!")

    @staticmethod
    def read_excel(req: ExcelReadSheetRequest) -> DataServiceStatus:
        """
        Read one sheet from an excel file.

        :param req:
        :return:
        """
        _, ext = os.path.splitext(req.path)
        ext = ext[1:]
        if ext in {"xls", "xlsx"}:
            em = ExcelManipulator(req.path)
            sheets: List[str] = cast(Any, em.get_sheet_names())
            currentSheet: str = sheets[0] if req.sheet is None else req.sheet
            res = em.read_sheet(currentSheet)
            resp = ExcelReadSheetResponse.create(df_to_json(res), currentSheet, sheets)
            return DataServiceStatus(status=DataServiceState.SUCCESS, msg="Read excel file succeeded!", data=resp)
        else:
            return DataServiceStatus(status=DataServiceState.ERROR,
                                     msg=f"File extension {ext} unsupported for excel files!")
