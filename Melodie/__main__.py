# -*- coding:utf-8 -*-
# @Time: 2021/9/23 16:52
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: __main__.py
import argparse
import copy
import os
import sys

from typing import Callable

parser = argparse.ArgumentParser()
parser.add_argument("action", help="""[serve] for starting the management server;
[run] for scanning code(NotImplemented)
""")
# parser.add_argument("", help="""[serve] for starting the management server;
# [run] for scanning code(NotImplemented)
# """)
args = parser.parse_args()
assert args.action in {'run', 'serve', 'create'}
if args.action == 'serve':
    from Melodie.management.manager_server import run

    run()
elif args.action == 'create':
    root = os.getcwd()
    import tkinter as tk
    from tkinter.simpledialog import askstring
    from tkinter.filedialog import askdirectory
    from tkinter.messagebox import showinfo, showwarning, showerror
    from Melodie.templates.create_template import create_routine, context


    def ask_str_input(hint: str, validator: Callable[[str], bool], error_hint: str) -> str:
        while 1:
            s = askstring('Fill up configurations', hint)
            if s is None:
                print('Create Project Routine Cancelled, routine exit.')
                sys.exit(0)
            if not validator(s):
                showerror('Error', error_hint.format(s=s))
            else:
                return s


    app = tk.Tk()  # 初始化GUI程序
    app.withdraw()  # 仅显示对话框，隐藏主窗口
    path_valid = False
    path = askdirectory(title='Where to create project: ')
    if path is None:
        print('Cancelled by user, routine exit.')
        sys.exit()
    project_name = ask_str_input('Project Name', lambda s: s.isidentifier(), 'Project name {s} is invalid!')
    context = copy.deepcopy(context)
    context['project_name'] = project_name
    context['project_alias'] = project_name
    context['project_text'] = project_name
    create_routine(path, context)
