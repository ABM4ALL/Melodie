# -*- coding:utf-8 -*-
import os
import sys
import Melodie


# os.system(
#     """autoflake -r --in-place --remove-unused-variables --exclude=__init__.py Melodie MelodieInfra tests"""
# )
os.system("isort -rc Melodie MelodieInfra tests")
os.system(f"{sys.executable} -m black .")
