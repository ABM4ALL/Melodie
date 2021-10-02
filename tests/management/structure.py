# -*- coding:utf-8 -*-
# @Time: 2021/10/2 11:50
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: structure.py
import os

from Melodie.management.project_structure import list_all_files


def test_list_files():
    files = list_all_files(os.path.dirname(os.path.dirname(__file__)), {'.py'})
    print(files)