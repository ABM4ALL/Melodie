# -*- coding:utf-8 -*-
# @Time: 2021/10/2 9:41
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: run_manager.py.py
import os.path

from Melodie.studio.main import studio_main

studio_main(os.path.join(os.getcwd(), ".melodieconfig"))
