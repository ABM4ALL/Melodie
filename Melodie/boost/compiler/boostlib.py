# -*- coding:utf-8 -*-
# @Time: 2021/10/20 9:09
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: boostlib.py.py
import numpy as np
import numba


@numba.njit
def ___agent___manager___random_sample(agent_manager: np.ndarray, num):
    return np.random.choice(agent_manager, num)


if __name__ == '__main__':
    agent_manager = np.array([('Rex', i, 81.0) for i in range(100)],
                             dtype=[('name', 'U10'), ('age', 'i4'), ('weight', 'f4')])
    sample = ___agent___manager___random_sample(agent_manager, 2)
    print(sample)
    print(agent_manager[0].name)
