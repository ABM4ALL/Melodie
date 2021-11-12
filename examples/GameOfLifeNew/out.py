
import random
import numpy as np
from Melodie.boost.compiler.boostlib import ___agent___manager___random_sample
import numba

@numba.jit
def ___agent___go_produce(___agent):
    rand = random.random()
    if (rand <= ___agent['productivity']):
        ___agent['account'] += 1
    else:
        pass
    return None


@numba.jit
def ___environment___step(___environment, agents: 'AgentList', network: 'Network'):
    for agent in agents:
        if (agent['status'] == 0):
            if (random.random() > agent['reliability']):
                agent['status'] = 1
        elif (random.random() > 0.6):
            agent['status'] = 0
        if (agent['status'] == 1):
            node = network.get_node_by_id(agent.id)
            neighbor_ids: 'np.ndarray' = network.get_neighbor_ids(node.id)
            for neighbor_id in neighbor_ids:
                if (random.random() > 0.97):
                    agents[neighbor_id].status = 1


@numba.jit
def ___environment___get_agents_statistic(___environment, agents: 'AgentList'):
    s = 0
    agent: 'Agent' = None
    for agent in agents:
        s += agent['status']
    print((s / 652))




def ___model___run(___model):
    agent_manager: 'AgentList' = ___model.agent_list
    for t in range(0, ___model.scenario.periods):
        ___environment___step(___model.environment, agent_manager, ___model.network)
    ___environment___get_agents_statistic(___model.environment, agent_manager)
