# -*- coding:utf-8 -*-
# @Time: 2021/10/3 21:00
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: test_lib.py

# coding: utf-8
# 这个import会先找hello.py，找不到就会找hello.so
import random
from typing import List
# import pygame

import numba

import hello  # 导入了hello.so
import time
import numpy as np


class A:
    def __init__(self):
        self.a = 0


l = [A() for i in range(10)]


class PyCell(hello.Cell):
    def __init__(self) -> None:
        super().__init__()
        self.a = 456


class PurePyCell():
    def __init__(self) -> None:
        self.x = 0
        self.y = 0
        self.a = 0


def python_get_attribute(lst: list):
    dim2 = len(lst[0])
    data = np.zeros((len(lst), dim2))
    for i in range(len(lst)):
        for j in range(dim2):
            data[i][j] = lst[i][j].a


@numba.njit
def convert_coor(x, y, xmax, ymax):
    if x >= xmax:
        x -= xmax
    elif x < 0:
        x = xmax + x
    if y >= ymax:
        y -= ymax
    elif y < 0:
        y = ymax + y - 1
    return x, y


@numba.njit
def get_neighbor_pos(x, y, xmax, ymax):
    neighbor_pos = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
    i = 0
    for dx, dy in neighbor_pos:
        neighbor_pos[i] = convert_coor(x + dx, y + dy, xmax, ymax)
        i += 1
    return neighbor_pos


def python_interact(lst: List[List[PurePyCell]]):
    dim1 = len(lst)
    dim2 = len(lst[0])
    # data = np.zeros((dim1, dim2))
    # try:
    for i in range(len(lst)):
        for j in range(dim2):
            neighbors_pos = get_neighbor_pos(i, j, dim2, dim1)
            count = 0
            this = lst[i][j]
            for pos in neighbors_pos:
                if lst[pos[1]][pos[0]].a == 1:
                    count += 1
            if count > 2:
                this.a = 0
            else:
                this.a = 1
    # except IndexError:
    #     print(pos)


@numba.njit(cache=True)
def numba_interact(arr):
    dim1, dim2 = arr.shape
    for i in range(dim1):
        for j in range(dim2):
            neighbor_pos = get_neighbor_pos(i, j, dim2, dim1)
            count = 0
            for pos in neighbor_pos:
                if arr[pos[1]][pos[0]] == 1:
                    count += 1
            # print(count)
            if count <= 1:
                arr[i][j] = 0
            elif count == 2:
                arr[i][j] = 1
            elif count == 3:
                if arr[i][j] == 1:
                    arr[i][j] = 1
                else:
                    arr[i][j] = 0
            else:
                arr[i][j] = 0
    return arr


def compare_collect_attribute_time():
    steps = 200

    t0 = time.time()
    for i in range(steps):
        python_get_attribute(pure_py_lst)

    t1 = time.time()

    for i in range(steps):
        res = hello.call_walk_position(lst, 'a')
    t2 = time.time()
    print(res)

    # hello.call_walk_position([[cell]])
    print('use_dll_time', t2 - t1, 'use_python_time', t1 - t0)


def compare_go_interaction_time():
    steps = 500
    # res = hello.call_walk_position(lst, 'a')
    # numba_interact(res)
    # hello.broadcast(lst, 'a', res)
    t0 = time.time()
    for i in range(steps):
        pass
        # python_interact(pure_py_lst)

    t1 = time.time()

    for i in range(steps):
        res = hello.call_walk_position(lst, 'a')
        numba_interact(res)
        hello.broadcast(lst, 'a', res)
    t2 = time.time()
    print(res)
    print('use_dll_time', t2 - t1, 'use_python_time', t1 - t0)


import matplotlib.pyplot as plt

XM = 400
YM = 400

pure_py_lst = [[PurePyCell() for i in range(XM)] for j in range(YM)]
lst = pure_py_lst

# 打开交互模式
plt.ion()
fig1 = plt.figure('frame')
i = 0
hello.broadcast(lst, 'a', np.random.randint(0, 2, (XM, YM)))
ax1 = fig1.add_subplot(1, 1, 1)
image = None
last_tick_time = time.time()
last_steps = 0
while 1:
    current_time = time.time()
    if current_time - last_tick_time > 1:
        last_tick_time = current_time
        fps = (i - last_steps)
        last_steps = i
        print('====================================current_step', i,'fps', fps)
    # ax1.axis('off')  # 关掉坐标轴
    t0 = time.time()
    res = hello.call_walk_position(lst, 'a')
    res = numba_interact(res)
    hello.broadcast(lst, 'a', res)
    t1 = time.time()
    print(t1 - t0)
    # res = np.random.randint(0, 255, (100, 100))
    if image is None:
        image = ax1.imshow(res * 255, cmap='gray')
    else:
        image.set_data(res * 255)

    plt.pause(0.001)
    i += 1
    # print(i)
    # 清除当前画布
    # fig1.clf()

plt.ioff()
