# import numpy as np
# import numba
#
#
# @numba.njit
# def f_on_one_item(item):
#     # for i in range(len()):
#     item.age = 21
#     # arr[i]['age'] = 20
#
#
# @numba.njit
# def f(arr):
#     for i in range(len(arr)):
#         arr[i].age = 20
#         # arr[i]['age'] = 20
#
# @numba.njit
# def f2(arr):
#     for a in arr:
#         a.age = 200
#         # arr[i]['age'] = 20
#
# # cannot process string!
# # @numba.njit
# # def f_str(arr):
# #     for a in arr:
# #         a.name = b'a'
#         # arr[i]['age'] = 20
# def main():
#     x = np.array([('Rex', 9, 81.0), ('Fido', 3, 27.0)],
#
#                  dtype=[('name', 'U10'), ('age', 'i4'), ('weight', 'f4')])
#     f(x)
#     f_on_one_item(x[0])
#     print(x)
#     f2(x)
#     print(x)
#     # f_str(x)
#     # print(x)
#
#
# if __name__ == '__main__':
#     main()
import random

import numpy as np

from Melodie import Scenario
from out import ___environment___go_money_produce, \
    ___environment___go_money_transfer, \
    ___environment___calc_wealth_and_gini, ___model___run

___environment = np.array([(100, 0.6, 0, 0)],
                          dtype=[('trade_num', 'i4'),
                                 ('win_prob', 'f4'),
                                 ('total_wealth', 'i4'),
                                 ('gini', 'f4')])

___agent_manager = np.array([(i, 0, 0.5) for i in range(300)],
                            dtype=[('id', 'i4'),
                                   ('account', 'f4'),
                                   ('productivity', 'f4'),
                                   ])
import time


def a(___environment, ___agent_manager):
    for i in range(200):
        ___environment___go_money_produce(___environment[0], ___agent_manager)

        ___environment___go_money_transfer(___environment[0], ___agent_manager)

        ___environment___calc_wealth_and_gini(___environment[0], ___agent_manager)


N = 300
t0 = time.time()


class Model1:
    def __init__(self):
        self.environment = np.array([(100, 0.6, 0, 0)],
                                    dtype=[('trade_num', 'i4'),
                                           ('win_prob', 'f4'),
                                           ('total_wealth', 'i4'),
                                           ('gini', 'f4')])[0]

        self.agent_manager = np.array([(i, 0, 0.5) for i in range(300)],
                                      dtype=[('id', 'i4'),
                                             ('account', 'f4'),
                                             ('productivity', 'f4'),
                                             ])
        # self.agent_manager = self.___agent_manager
        # self.environment = self.___environment
        self.scenario = Scenario()
        self.scenario.periods = 200


for i in range(N):
    model1 = Model1()
    ___model___run(model1)
    # a(___environment, ___agent_manager)
t1 = time.time()
print(t1 - t0, (t1 - t0) / N)
