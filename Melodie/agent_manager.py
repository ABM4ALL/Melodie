import random

import pandas as pd

from typing import Dict, TYPE_CHECKING, ClassVar, List, Tuple, Callable, Union
from .basic import AgentGroup, SortedAgentIndex, parse_watched_attrs, IndexedAgentList, MelodieExceptions

if TYPE_CHECKING:
    from .agent import Agent
    from .run import DataCollector


class AgentManager:
    def __init__(self, agent_class: ClassVar['Agent'], length: int) -> None:
        # from .agent import Agent
        # assert issubclass(agent_class, Agent)
        self._iter_index = 0
        self.agent_class: ClassVar['Agent'] = agent_class
        self.initial_agent_num: int = length
        self.agents = self.setup_agents()

        self.setup()

    def __len__(self):
        return len(self.agents)

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

    def random_sample(self, sample_num: int):
        return random.sample(self.agents, sample_num)

    def query(self, condition: Callable[['Agent'], bool]) -> List['Agent']:
        """
        How to implement this method?
        :return:
        """

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
            data_list.append({k: agent.__dict__[k] for k in column_names})
        df= pd.DataFrame(data_list)
        df['id'] = df['id'].astype(int)
        return df