# -*- coding:utf-8 -*-
# @Time: 2021/10/20 20:21
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: config.py
import os

from Melodie import Config, Model, Scenario

cfg = Config(
    'test',
    os.path.dirname(__file__),
    excel_source_folder=os.path.join(os.path.dirname(__file__), 'resources', 'excels'),
    sqlite_folder=os.path.join(os.path.dirname(__file__), 'resources', 'db'),
    output_folder=os.path.join(os.path.dirname(__file__), 'resources', 'output')
)

cfg_for_temp = Config(
    'temp_db_created',
    os.path.dirname(__file__),
    excel_source_folder=os.path.join(os.path.dirname(__file__), 'resources', 'excels'),
    sqlite_folder=os.path.join(os.path.dirname(__file__), 'resources', 'temp'),
    output_folder=os.path.join(os.path.dirname(__file__), 'resources', 'output')
)

model = Model(cfg, Scenario())
