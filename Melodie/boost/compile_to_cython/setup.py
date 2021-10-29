# -*- coding:utf-8 -*-
# @Time: 2021/10/29 9:54
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: setup.py.py


import numpy as np
from setuptools import setup
from distutils.extension import Extension
from Cython.Build import cythonize
from Cython.Distutils import build_ext

ext_modules = [
    Extension("demo", ["demo.pyx"]),
    Extension("basicmath", ['basicmath.pyx'])
]

setup(
    cmdclass={"build_ext": build_ext},
    ext_modules=ext_modules,
    include_dirs=[np.get_include()]
)

# from demo import helper
#
# helper()
