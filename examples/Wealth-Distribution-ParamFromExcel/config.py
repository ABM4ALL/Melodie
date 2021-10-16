# -*- coding:utf-8 -*-
# @Time: 2021/10/16 17:09
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: config.py.py
import os

from Melodie import Config

config = Config('WealthDistribution', os.path.dirname(__file__),
                parameters_source='from_file',
                parameters_xls_file='params.xlsx',
                static_xls_files=['static1.xlsx', 'static2.xlsx'])
