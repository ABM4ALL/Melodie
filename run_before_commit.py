# -*- coding:utf-8 -*-
import os
import sys
import Melodie


os.system(
    """autoflake -r --in-place --remove-unused-variables \
		--remove-all-unused-imports --exclude=__init__.py SkyStaticAnalysis demos tests"""
)
os.system("isort -rc SkyStaticAnalysis demos tests")
os.system(f"{sys.executable} -m black .")
