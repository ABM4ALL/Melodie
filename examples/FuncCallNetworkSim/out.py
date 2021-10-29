
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
def ___environment___step(___environment, agents: 'AgentManager', network: 'Network'):
    for agent in agents:
        if (agent['status'] == 0):
            if (random.random() > agent['reliability']):
                agent['status'] = 1
                neighbors_ids: 'np.ndarray' = network.get_neighbor_ids(agent.id)
                if (neighbors_ids is not None):
                    for neighbor_ids in neighbors_ids:
                        agents[neighbor_ids].status = 1




def ___model___run(___model):
    agent_manager = ___model.agent_manager
    for t in range(0, ___model.scenario.periods):
        ___environment___step(___model.environment, agent_manager, ___model.network)
