import sys


def is_pypy():
    return sys.version.lower().find("pypy") != -1
