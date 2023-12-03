import os
import sys

basedir = os.path.dirname(__file__)
sys.path.append(os.path.dirname(basedir))
OUTPUT_DIR = os.path.join(basedir, "out")
if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)


def is_pypy():
    return sys.version.lower().find("pypy") != -1
