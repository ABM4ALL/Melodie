# -*- coding:utf-8 -*-
# @Time: 2023/5/2 17:20
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: dependencies.py

try:
    import numpy as np
    import pandas as pd
except:

    class np:
        ndarray = None

    class pd:
        DataFrame = None
