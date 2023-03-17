# -*- coding:utf-8 -*-
# @Time: 2023/2/8 19:28
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: web.py
from flask import send_file, Response
from ..models.web import DataServiceStatus, DataServiceState


def create_json_response(data) -> str:
    return DataServiceStatus(DataServiceState.SUCCESS, data=data).to_json()


def create_failed_response(msg: str) -> str:
    return DataServiceStatus(DataServiceState.ERROR, msg=msg).to_json()


def create_file_response(filename: str) -> Response:
    return send_file(filename)
