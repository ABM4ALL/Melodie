from typing import Callable, List

import numpy as np
from sko.GA import GA

from Melodie import Agent


class NewAgent(Agent):
    def __init__(self, agent_id):
        super(NewAgent, self).__init__(agent_id)
        self.param_0 = 0
        self.param_1 = 1


def schaffer(p):
    '''
    This function has plenty of local minimum, with strong shocks
    global minimum at (0,0) with value 0
    https://en.wikipedia.org/wiki/Test_functions_for_optimization
    '''
    x1, x2 = p
    part1 = np.square(x1) - np.square(x2)
    part2 = np.square(x1) + np.square(x2)
    return 0.5 + (np.square(np.sin(part1)) - 0.5) / np.square(1 + 0.001 * part2)


target_function_value_this_step = []


def get_result(agent_id: int) -> Callable[[np.ndarray], float]:
    global target_function_value_this_step

    def f(p):
        a = target_function_value_this_step[agent_id]
        return schaffer(p)

    return f


ga1 = GA(func=get_result(0), n_dim=2, size_pop=50, max_iter=80, prob_mut=0.001, lb=[-1, -1], ub=[1, 1], precision=1e-5)
ga2 = GA(func=get_result(1), n_dim=2, size_pop=50, max_iter=80, prob_mut=0.001, lb=[-1, -1], ub=[1, 1], precision=1e-5)
ga_list: List[GA] = [ga1, ga2]
al = [NewAgent(i) for i in range(2)]
for i in range(80):
    target_function_value_this_step = []
    for chrome_id in range(50):
        for agent_index, ga_obj in enumerate(ga_list):  # 依次获得每个agent的值。
            params = ga_obj.chrom2x(ga_obj.Chrom)[chrome_id]
            al[agent_index].param_0 = params[0]
            al[agent_index].param_1 = params[1]
        # 在这里运行模型。

        # 在这里运行当前步的目标函数。外层为染色体id, 内层为当前agent的目标值。

        target_function_value_this_step.append([agent.param_0 * agent.param_1 for agent in al])

        # 这样可以刷新这些值。




    best_x, best_y = ga1.run(1)
    best_x, best_y = ga2.run(1)
    print('best_x:', best_x, '\n', 'best_y:', best_y)
    print(ga1.Chrom.shape)  # (50,36). 第一个索引是一条染色体，第二个索引是
    print(ga1.chrom2x(ga1.Chrom))  # (50, 2).第一个索引是染色体，第二个索引是一个整数。
# %% Plot the result
import pandas as pd
import matplotlib.pyplot as plt

Y_history = pd.DataFrame(ga1.all_history_Y)
fig, ax = plt.subplots(2, 1)
ax[0].plot(Y_history.index, Y_history.values, '.', color='red')
Y_history.min(axis=1).cummin().plot(kind='line')
plt.show()
