# -*- coding:utf-8 -*-
# @Time: 2021/10/3 21:00
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: test_lib.py

# coding: utf-8
# To run this example, install numba, PyQt6 and pyqtgraph for visualization performance.


import numba

from Melodie.boost import broadcast_2d, gather_2d  # 导入了hello.so

from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import pyqtgraph as pg
import pyqtgraph.ptime as ptime


class PurePyCell():
    def __init__(self) -> None:
        self.x = 0
        self.y = 0
        self.a = 0


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


@numba.njit
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


XM = 200
YM = 200

pure_py_lst = [[PurePyCell() for i in range(YM)] for j in range(XM)]
lst = pure_py_lst

app = pg.mkQApp("ImageItem Example")

win = pg.GraphicsLayoutWidget()
win.show()
win.setWindowTitle('pyqtgraph example: ImageItem')
view = win.addViewBox()

view.setAspectLocked(True)

img = pg.ImageItem(border='w')
view.addItem(img)

view.setRange(QtCore.QRectF(0, 0, XM, YM))

i = 0

updateTime = ptime.time()
fps = 0

timer = QtCore.QTimer()

broadcast_2d(lst, 'a', np.random.randint(0, 2, (XM, YM)))  # Initialize the pycells with random 0 and 1


def updateData():
    global img, data, i, updateTime, fps

    res = gather_2d(lst, 'a')
    res = numba_interact(res)
    broadcast_2d(lst, 'a', res)

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
