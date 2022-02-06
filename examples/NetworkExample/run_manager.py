# -*- coding:utf-8 -*-
# @Time: 2021/10/2 9:41
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: run_studio.py.py
import os

from Melodie.studio.main import studio_main
from config import config

studio_main(os.path.join(os.getcwd(), ".melodieconfig"), config)
