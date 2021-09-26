# -*- coding:utf-8 -*-
# @Time: 2021/9/24 11:24
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: pil_gen.py

from PIL import Image
import numpy as np

size = (600, 600)

xv, yv = np.meshgrid(np.linspace(-10, 10, 600), np.linspace(-10, 10, 600))
vals = np.zeros(size, dtype=float)
colored_vals = np.zeros((size[0], size[1], 3), dtype=float)
# print(grid)
for i in range(size[0]):
    for j in range(size[1]):
        vals[i][j] = (xv[i][j] ** 2 + yv[i][j] ** 2) ** 0.5

print(vals)
vals = vals / (np.max(vals) - np.min(vals)) * 255

for i in range(size[0]):
    for j in range(size[1]):
        colored_vals[i][j][0] = (255 - vals[i][j])
        colored_vals[i][j][1] = (vals[i][j] - 255)
print(colored_vals)
img = Image.fromarray(np.uint8(colored_vals), mode='RGB')
img.show()
img.save('img.png')