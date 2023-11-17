import random
from typing import Any, Type, List, Dict

import pandas as pd

from MelodieInfra.table.pandas_compat import TableInterface, TABLE_TYPE


def set_agent_params(agent, params):
    for k, v in params.items():
        setattr(agent, k, v)


def set_properties(agent_cls, agent_list, props_table: TABLE_TYPE):
    """
    Set parameters of all agents in current scenario from a pandas dataframe.

    :return: None
    """
    table = TableInterface(props_table)

    param_names = [param for param in table.columns if param not in {"id_scenario"}]

    if "id_scenario" in table.columns:
        params_table = table.filter(
            lambda row: row["id_scenario"] == agent_list.scenario.id
        )
    else:
        params_table = table  # deep copy this dataframe.
    if "id" in param_names:
        row: Dict[str, Any]
        for i, row in enumerate(params_table.iter_dicts()):
            params = {k: row[k] for k in param_names}
            agent = agent_list.get_agent(params["id"])
            print(agent)
            if agent is None:
                agent = agent_list.add(None)
            # print(params)
            set_agent_params(agent, params)
            print(agent.id, agent.a)
    else:
        row: Dict[str, Any]
        params_table.df.data("out.csv")
        assert len(agent_list) == len(params_table), (
            len(agent_list),
            len(params_table),
        )

        for i, row in enumerate(params_table.iter_dicts()):
            params = {k: row[k] for k in param_names}
            agent = agent_list.agents(i)
            set_agent_params(agent, params)


def create_class(agent_cls: Type):
    from numba import types, typed, jit, njit
    import numpy as np

    spec = [
        ("_id_offset", types.int64),
        ("agents", types.ListType(agent_cls.class_type.instance_type)),
        ("indices", types.DictType(types.int64, types.int64)),
    ]

    # @jit(nopython=False)
    # def create_agent_class():
    #     return agent_cls

    @njit(cache=True)
    def rand_choice(length, sample_num):
        return np.random.choice(length, sample_num)

    @njit(cache=True)
    def create_empty_int2int_dict():
        return typed.Dict.empty(types.int64, types.int64)

    @jitclass(spec)
    class JittedAgentList:
        def __init__(self) -> None:
            self._id_offset = -1
            self.agents = typed.List([agent_cls(0) for i in range(0)])
            self.indices = create_empty_int2int_dict()

        def new_id(self) -> int:
            self._id_offset += 1
            return self._id_offset

        def add(self, agent):
            if agent is None:
                agent = agent_cls(self.new_id())
            self.agents.append(agent)
            index = len(self.agents) - 1
            self._set_index(agent.id, index)
            return agent

        def get_agent(self, agent_id: int):
            index = self._get_index(agent_id)
            if index == -1:
                return None
            else:
                return self.agents[index]

        def _set_index(self, agent_id, agent_index):
            self.indices[agent_id] = agent_index

        def _get_index(self, agent_id):
            if agent_id in self.indices:
                return self.indices[agent_id]
            else:
                return -1

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

    @jitclass([("id", int64), ("a", float64)])
    class JittedAgent:
        def __init__(self, id: int) -> None:
            self.id = id
            self.a = 0.5

    cls = create_class(JittedAgent)
    agents = cls()
    agents.add(JittedAgent(0))
    agents.add(JittedAgent(2))
    agents.add(JittedAgent(3))
    agents.add(None)
    print(iter(agents))
    print(agents.agents[0].a)
    print(len(agents))
    print(agents.indices)
    print(agents._get_index(3))
    print(agents[1].id)
    assert agents[1].id == agents.get_agent(agents[1].id).id
    agent1, agent2 = agents.random_sample(2)
    print(agent1.id, agent2.id)

    @njit
    def f(a):
        return a.id >= 2

    filtered_agents = agents.filter(f)
    print(filtered_agents)
    print(filtered_agents[0].id)
    t1 = time.time()

    agents = cls()
    props_table = pd.DataFrame([[0, 1], [1, 114]], columns=["id", "a"])
    set_properties(JittedAgent, agents, props_table)
    print(len(agents.agents))
    print(agents.agents[0].id, agents.agents[1].id)
    print("warming up time", t1 - t0)
