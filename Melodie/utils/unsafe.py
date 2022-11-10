# -*- coding:utf-8 -*-
# @Time: 2022/11/10 14:36
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: unsafe.py

class Unsafe:
    @staticmethod
    def create_getter_by_str(rvalue_expr):
        func_str = f"""
def getter(scenario):
    return {rvalue_expr}
        """
        local_vars = {}
        exec(func_str, {}, local_vars)
        return local_vars['getter']

    @staticmethod
    def create_setter_by_str(lvalue_expr):
        func_str = f"""
def setter(scenario, value):
    {lvalue_expr} = value
        """
        local_vars = {}
        exec(func_str, {}, local_vars)
        return local_vars['setter']
