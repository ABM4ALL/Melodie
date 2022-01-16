# -*- coding:utf-8 -*-
# @Time: 2021/10/6 13:29
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: cookiecutter.py.py
import os.path
import datetime

from cookiecutter.main import cookiecutter

directory = os.path.dirname(__file__)
context = {
    "author": "Anonymous",
    "email": "AnonymousUser@never.contact.me.com",
    "created_at": datetime.time(),

    "project_name": "MyProject",
    "project_alias": "My",
    "project_text": "我的项目",
    "file_name": "Howdy",
    "greeting_recipient": "Andy",
}


def remove_unused_files(root, file_status):
    paths_to_del = []
    for name, status in file_status.items():
        if isinstance(status, bool):
            path = os.path.join(root, name)
            if not status:
                paths_to_del.append(path)
        elif isinstance(status, dict):
            for file_name, sub_stat in status.items():
                if not status[file_name]:
                    path = os.path.join(root, name, file_name)
                    paths_to_del.append(path)
        elif isinstance(status, str):
            prev_name = os.path.join(root, name)
            post_name = os.path.join(root, status)
            os.rename(prev_name, post_name)
            print('renamed data', prev_name, 'to', post_name)
        else:
            raise TypeError(status)

    for path in paths_to_del:
        if os.path.exists(path):
            print('removed data,', path)
            os.remove(path)
        else:
            print('data ', path, ' should be removed but it was not exist! ')


def create_routine(directory: str, extra_context):
    file_status_with_excel = {
        "README.md": True,
        extra_context["project_name"]: {
            "agent.py": True,
            "validation.py": True,
            "data_collector.py": True,
            "environment.py": True,
            "model.True": True,
            "register.rst.py": False,
            "register.rst.py": True,
            "table_generator.py": False
        },
        "model": True,
        'run_with_excel.py': 'run.py',
        "run_advanced.py": False
    }
    cookiecutter((os.path.join(os.path.dirname(__file__), 'ProjectTemplate')),
                 no_input=True,
                 extra_context=extra_context, output_dir=directory)

    os.chdir(os.path.join(directory, extra_context['project_text']))
    root = os.getcwd()

    remove_unused_files(root, file_status_with_excel)
    pass


if __name__ == "__main__":
    file_status_with_excel = {
        "README.md": True,
        context["project_name"]: {
            "agent.py": True,
            "validation.py": True,
            "data_collector.py": True,
            "environment.py": True,
            "model.True": True,
            "register.rst.py": False,
            "register.rst.py": True,
            "table_generator.py": False
        },
        "model": True,
        'run_with_excel.py': 'run.py',
        "run_advanced.py": False
    }
    create_routine(directory, context, file_status_with_excel)
