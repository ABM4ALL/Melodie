# -*- coding:utf-8 -*-
import os
import sys

os.system(f"{sys.executable} -m black .")
os.system("pytest")
