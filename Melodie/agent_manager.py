import random

import pandas as pd

from typing import TYPE_CHECKING, ClassVar, List
from .basic import IndexedAgentList, MelodieExceptions

if TYPE_CHECKING:
    from .agent import Agent


class AgentManager:
    """
    TODO:建议改成AgentList(相对不太紧要)
    Songmin: 如果不想跟agentpy重名的话，或者叫AgentContainer也行？主要是Manager给人一种要“组织agent干点儿啥”的感觉，那个是environment的事儿。
    """
    def __init__(self, agent_class: ClassVar['Agent'], length: int) -> None:
        self._iter_index = 0
        self.agent_class: ClassVar['Agent'] = agent_class
        self.initial_agent_num: int = length
        self.agents = self.setup_agents()

        self.setup()

    def __len__(self):
        return len(self.agents)

    def __getitem__(self, item):
        return self.agents.__getitem__(item)

    def __iter__(self):
        self._iter_index = 0
        return self

    def __next__(self):
        # print(len(self.agents),self._iter_index)
        if self._iter_index < len(self.agents):
            elem = self.agents[self._iter_index]
            self._iter_index += 1
            return elem
        else:
            raise StopIteration

    def setup(self):
        pass

    def setup_agents(self) -> IndexedAgentList:
        agents = [self.agent_class(i) for i in range(self.initial_agent_num)]
        for agent in agents:
            agent.setup()
        return IndexedAgentList(agents)

    def random_sample(self, sample_num: int) -> 'Agent':
        return random.sample(self.agents, sample_num)

    def remove(self, agent: 'Agent'):
        for i, a in enumerate(self.agents):
            if a is agent:
                self.agents.pop(i)
                break

    def add(self, agent: 'Agent'):
        self.agents.add(agent)

    def to_dataframe(self, column_names: List[str] = None) -> pd.DataFrame:
        """
        Store all agent values to dataframe.
        This method is always called by the data collector.

        :param column_names: property names to store
        :return:
        """
        protected_columns = ['id']
        data_list = []
        if len(self.agents) == 0:
            raise MelodieExceptions.Agents.AgentManagerEmpty(self)

        if column_names is None:
            column_names = list(self.__dict__.keys())
        column_names = protected_columns + column_names
        agent0 = self.agents[0]
        for column_name in column_names:
            if column_name not in agent0.__dict__.keys():
                raise MelodieExceptions.Agents.AgentPropertyNameNotExist(column_name, agent0)
        for agent in self.agents:
            d = {k: agent.__dict__[k] for k in column_names}
            data_list.append(d)
        df = pd.DataFrame(data_list)
        df['id'] = df['id'].astype(int)
        return df
