
import random
from typing import Type, List


def create_class(agent_cls: Type):
    from numba import types, typed, jit
    import numpy as np
    spec = [
        ("agents", types.ListType(agent_cls.class_type.instance_type)),
        ("indices", types.DictType(types.int64, types.int64))
    ]

    @jit(cache=True)
    def rand_choice(length, sample_num):
        return np.random.choice(length, sample_num)

    @jit(cache=True)
    def create_empty_int2int_dict():
        return typed.Dict.empty(types.int64, types.int64)

    @jitclass(spec)
    class JittedAgentList:
        def __init__(self) -> None:
            self.agents = typed.List([agent_cls(0) for i in range(0)])
            self.indices = create_empty_int2int_dict()

        def add(self, agent):
            self.agents.append(agent)
            index = len(self.agents)-1
            self._set_index(agent.id, index)

        def _set_index(self, agent_id, agent_index):
            self.indices[agent_id] = agent_index

        def _get_index(self, agent_id):
            return self.indices[agent_id]

        def __getitem__(self, agent_index):
            return self.agents[agent_index]

        def __len__(self):
            return len(self.agents)

        def random_sample(self, sample_num: int) -> List["AgentGeneric"]:
            """
            Randomly sample `sample_num` agents from the container
            :param sample_num:
            :return:
            """
            indices = rand_choice(len(self.agents), sample_num)
            agents = typed.List([agent_cls(0) for i in range(0)])
            for index in indices:
                agents.append(self.agents[index])
            return agents

        def filter(self, f):
            agents = typed.List([agent_cls(0) for i in range(0)])
            for a in self.agents:
                if f(a):
                    agents.append(a)
            return agents

    return JittedAgentList


if __name__ == "__main__":
    from numba import float64, int64, njit
    from numba.experimental import jitclass
    import time

    t0 = time.time()

    @jitclass([
        ("id", int64),
        ("a", float64)
    ])
    class JittedAgent:
        def __init__(self, id: int) -> None:
            self.id = id
            self.a = 0.5

    cls = create_class(JittedAgent)
    agents = cls()
    agents.add(JittedAgent(0))
    agents.add(JittedAgent(2))
    agents.add(JittedAgent(3))
    print(agents.agents[0].a)
    print(len(agents))
    print(agents.indices)
    print(agents._get_index(3))
    print(agents[1].id)
    agent1, agent2 = agents.random_sample(2)
    print(agent1.id, agent2.id)

    @njit
    def f(a):
        return a.id >= 2
    filtered_agents = agents.filter(f)
    print(filtered_agents)
    print(filtered_agents[0].id)
    t1 = time.time()
    print("warming up time", t1 - t0)
