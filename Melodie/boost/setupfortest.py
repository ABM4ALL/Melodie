# -*- coding:utf-8 -*-
# @Time: 2021/10/6 22:03
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: setup_for_test.py.py

from distutils.core import setup
from Cython.Build import cythonize

setup(name='Hello world app',
      ext_modules=cythonize("_test_features.pyx",annotate=True))