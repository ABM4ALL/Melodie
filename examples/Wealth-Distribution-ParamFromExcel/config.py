# -*- coding:utf-8 -*-
# @Time: 2021/10/16 17:09
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: simulator_config.py.py
import os

from Melodie import NewConfig

config = NewConfig(
    'WealthDistribution',
    os.path.dirname(__file__),
    'data/sqlite',
    'data/excel_source',
    'data/csv',
)
