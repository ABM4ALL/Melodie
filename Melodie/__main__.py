# -*- coding:utf-8 -*-
# @Time: 2021/9/23 16:52
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: __main__.py
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("action", help="""[serve] for starting the management server;
[run] for scanning code(NotImplemented)
""")

args = parser.parse_args()
assert args.action in {'studio'}
if args.action == 'studio':
    from Melodie.studio.main import studio_main

    studio_main()
