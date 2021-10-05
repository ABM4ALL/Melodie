# -*- coding:utf-8 -*-
# @Time: 2021/10/3 21:00
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: test_lib.py

from Melodie.boost import py_broadcast_2d, py_gather_2d, broadcast_2d, gather_2d
import time


class PurePyCell():
    def __init__(self) -> None:
        self.x = 0
        self.y = 0
        self.a = 1
        self.b = 0.1


XM = 100
YM = 100

pure_py_lst = [[PurePyCell() for i in range(XM)] for j in range(YM)]
lst = pure_py_lst


def python_get_attribute(lst: list):
    dim2 = len(lst[0])
    # data = np.zeros((len(lst), dim2))
    for i in range(len(lst)):
        for j in range(dim2):
            lst[i][j].a


def compare_collect_attribute_time():
    steps = 200

    t0 = time.time()
    for i in range(steps):
        py_gather_2d(pure_py_lst, 'a')

    t1 = time.time()

    for i in range(steps):
        res = gather_2d(lst, 'a')
        res += 3
        broadcast_2d(lst, 'a', res)
    t2 = time.time()
    print(res)
    for i in range(steps):
        res = gather_2d(lst, 'b')
        res += 1
        broadcast_2d(lst, 'b', res)
    t3 = time.time()
    print(res)
    print('use_dll_gather_float', t3 - t2, 'use_dll_gather_int', t2 - t1, 'use_python_time', t1 - t0)


def test_benchmark():
    compare_collect_attribute_time()

if __name__=='__main__':
    compare_collect_attribute_time()