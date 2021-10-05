# -*- coding:utf-8 -*-
# @Time: 2021/10/3 20:59
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: setup.py.py
# file: setup.py
from distutils.core import setup
from Cython.Build import cythonize
import numpy as np

setup(name='Hello world app',
      ext_modules=cythonize("hello.pyx", annotate=True),
      include_dirs=[np.get_include()]
      )
