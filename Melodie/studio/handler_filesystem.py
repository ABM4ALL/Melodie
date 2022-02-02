# -*- coding:utf-8 -*-
# @Time: 2021/11/16 10:53
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: handler_charts.py
import json
import os.path

from flask import Blueprint, request
from .file_manager import JSONManager
from .messages import Response
from .config_manager import get_config_manager

file_system = Blueprint('fs', __name__)


def get_all_file_items(directory: str):
    items = []
    for root, dirs, files in os.walk(directory):
        if not os.path.samefile(root, directory):
            continue
        else:
            for file in files:
                items.append({'name': file, 'type': 'file'})
            for dir_name in dirs:
                items.append({'name': dir_name, 'type': 'directory'})

    return items


@file_system.route('getFSItems')
def all_fs_items():
    directory: str = request.args.get("directory")
    if directory == '':
        directory = os.path.join(os.path.expanduser('~'), 'Desktop')
    if os.path.exists(directory):
        return Response.ok({"currentDirectory": directory,
                            "fsItemsList": get_all_file_items(directory)})
    else:
        return Response.error(f"Directory {directory} does not exist!")


@file_system.route('gotoParentDir')
def go_to_parent():
    directory: str = request.args.get('directory')
    if directory == '':
        directory = os.path.join(os.path.expanduser('~'), 'Desktop')
    directory = os.path.dirname(directory)
    return Response.ok({"currentDirectory": directory,
                 "fsItemsList": get_all_file_items(directory)})


@file_system.route('gotoSubDir')
def go_to_sub():
    directory: str = request.args.get('directory')
    subdir: str = request.args.get('subdir')
    if directory == '':
        directory = os.path.join(os.path.expanduser('~'), 'Desktop')
    directory = os.path.join(directory, subdir)
    return Response.ok({"currentDirectory": directory,
                 "fsItemsList": get_all_file_items(directory)})
