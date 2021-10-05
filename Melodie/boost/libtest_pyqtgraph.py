# -*- coding:utf-8 -*-
# @Time: 2021/10/3 21:00
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: test_lib.py

# coding: utf-8
# 这个import会先找hello.py，找不到就会找hello.so

from typing import List

import numba

import hello  # 导入了hello.so
import time

numba.set_num_threads(2)


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
        x = xmax + x - 1
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


#
# print(numba.config.NUMBA_NUM_THREADS)
@numba.njit()
def numba_interact(arr):
    xmax, ymax = arr.shape
    new_arr = np.copy(arr)
    for x in numba.prange(xmax):
        for y in range(ymax):
            neighbor_pos = get_neighbor_pos(x, y, xmax, ymax)
            count = 0
            for pos in neighbor_pos:
                if arr[pos[0]][pos[1]] == 1:
                    count += 1

            this_alive = arr[x][y] == 1
            new_alive = False
            if this_alive:
                if count == 2 or count == 3:
                    new_alive = True
                else:
                    new_alive = False
            else:
                if count == 3:
                    new_alive = True
                else:
                    new_alive = False
            new_arr[x][y] = new_alive
    return new_arr


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

    t1 = time.time()

    for i in range(steps):
        res = hello.call_walk_position(lst, 'a')
        numba_interact(res)
        hello.broadcast(lst, 'a', res)
    t2 = time.time()
    print(res)
    print('use_dll_time', t2 - t1, 'use_python_time', t1 - t0)


XM = 300
YM = 400

pure_py_lst = [[PurePyCell() for i in range(XM)] for j in range(YM)]
lst = pure_py_lst

from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import pyqtgraph as pg
import pyqtgraph.ptime as ptime

app = pg.mkQApp("ImageItem Example")

## Create window with GraphicsView widget
win = pg.GraphicsLayoutWidget()
win.show()  ## show widget alone in its own window
win.setWindowTitle('pyqtgraph example: ImageItem')
view = win.addViewBox()

## lock the aspect ratio so pixels are always square
view.setAspectLocked(True)

## Create image item
img = pg.ImageItem(border='w')
view.addItem(img)

## Set initial view bounds
view.setRange(QtCore.QRectF(0, 0, XM, YM))

## Create random image
# data = np.random.normal(size=(15, 600, 600), loc=1024, scale=64).astype(np.uint16)
i = 0

updateTime = ptime.time()
fps = 0

timer = QtCore.QTimer()
# timer.setSingleShot(True)

# not using QTimer.singleShot() because of persistence on PyQt. see PR #1605

# data = np.zeros((XM, YM)).astype(np.uint16)
hello.broadcast(lst, 'a', np.random.randint(0, 2, (XM, YM)))


def updateData():
    global img, data, i, updateTime, fps


    res = hello.call_walk_position(lst, 'a')
    res = numba_interact(res)
    hello.broadcast(lst, 'a', res)

    data = res.astype(np.uint8).transpose()
    np.flip(data)
    img.setImage(data)

    # timer.start(1)
    now = ptime.time()
    fps2 = 1.0 / (now - updateTime)
    updateTime = now
    fps = fps * 0.9 + fps2 * 0.1

    print("%0.1f fps" % fps)


timer.timeout.connect(updateData)
timer.start(1)
updateData()

if __name__ == '__main__':
    pg.exec()
