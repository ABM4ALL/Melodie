import time

import numpy as np

from Melodie import Scenario
from out import ___model___run

N = 100


class Model1:
    def __init__(self):
        self.environment = np.array([(100, 0.6, 0, 0)],
                                    dtype=[('trade_num', 'i4'),
                                           ('win_prob', 'f4'),
                                           ('total_wealth', 'i4'),
                                           ('gini', 'f4')])[0]

        self.agent_list = np.array([(i, 0, 0.5) for i in range(300)],
                                   dtype=[('id', 'i4'),
                                          ('account', 'f4'),
                                          ('productivity', 'f4'),
                                          ])

        self.scenario = Scenario()
        self.scenario.periods = 200


model1 = Model1()
___model___run(model1)
t0 = time.time()
for i in range(N):
    model1 = Model1()
    ___model___run(model1)

t1 = time.time()
print(t1 - t0, f"模型迭代{N}次", "每次运行模型花费时间", (t1 - t0) / N)

# 以基尼系数为例，在i5-8250U CPU上，单次最快可以跑到0.0062s。
# 这个速度是非常快的，相当于速度提升了40倍。
