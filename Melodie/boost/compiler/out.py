import random
import numpy as np
from Melodie.boost.compiler.boostlib import ___agent___manager___random_sample
import numba


@numba.jit
def ___agent___go_produce(___agent):
    rand = np.random.random()
    if (rand <= ___agent['productivity']):
        ___agent['account'] += 1
    else:
        pass
    return None


@numba.jit
def ___environment___go_money_produce(___environment, agent_list: 'AgentManager'):
    al = agent_list
    for agent in al:
        ___agent___go_produce(agent)
    return None


@numba.jit
def ___environment___go_give_money(___environment, agent_from: 'GINIAgent', agent_to: 'GINIAgent'):
    if (agent_from['account'] == 0):
        pass
    else:
        agent_from['account'] -= 1
        agent_to['account'] += 1
    return None


@numba.jit
def ___environment___go_money_transfer(___environment, agent_list: 'AgentManager'):
    trade_num = ___environment['trade_num']
    for sub_period in range(0, int(trade_num)):
        agents = ___agent___manager___random_sample(agent_list, 2)
        agent_1: 'Agent' = agents[0]
        agent_2: 'Agent' = agents[1]
        who_win = 0
        rand = random.random()
        RICH = 0
        POOR = 1
        if (rand <= ___environment['win_prob']):
            who_win = RICH
        else:
            who_win = POOR
        if ((agent_1['account'] >= agent_2['account']) and (who_win == RICH)):
            ___environment___go_give_money(___environment, agent_2, agent_1)
        elif ((agent_1['account'] < agent_2['account']) and (who_win == RICH)):
            ___environment___go_give_money(___environment, agent_1, agent_2)
        elif ((agent_1['account'] >= agent_2['account']) and (who_win == POOR)):
            ___environment___go_give_money(___environment, agent_1, agent_2)
        elif ((agent_1['account'] < agent_2['account']) and (who_win == POOR)):
            ___environment___go_give_money(___environment, agent_2, agent_1)
        else:
            pass
    return None


@numba.jit
def ___environment___calc_gini(___environment, account_list: 'np.ndarray'):
    N = len(account_list)
    s = 0
    i = 0
    for xi in account_list:
        s += (xi * (N - i))
        i += 1
    B = (s / (N * np.sum(account_list)))
    return ((1 + (1 / N)) - (2 * B))


@numba.jit
def ___environment___calc_wealth_and_gini(___environment, AgentList: 'AgentManager'):
    account_list: 'np.ndarray' = np.zeros(len(AgentList))
    i = 0
    for agent in AgentList:
        account_list[i] = agent['account']
        i += 1
    ___environment['total_wealth'] = sum(account_list)
    ___environment['gini'] = ___environment___calc_gini(___environment, account_list)
    return None


def ___model___run(___model):
    for t in range(0, ___model.scenario.periods):
        ___environment___go_money_produce(___model.environment, ___model.agent_manager)
        ___environment___go_money_transfer(___model.environment, ___model.agent_manager)
        ___environment___calc_wealth_and_gini(___model.environment, ___model.agent_manager)
