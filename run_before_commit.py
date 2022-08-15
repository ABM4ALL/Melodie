# -*- coding:utf-8 -*-
import os
import sys
import Melodie

os.system(f"{sys.executable} -m black .")
os.system("pytest -s")
