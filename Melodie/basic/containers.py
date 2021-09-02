from typing import Callable, Dict, List, TYPE_CHECKING, Union, Tuple

from .algorithms import binary_search

if TYPE_CHECKING:
    from ..Agent import Agent


class AgentSet:
    def __init__(self, agents) -> None:
        self.agents_dic: Dict[int, 'Agent'] = {
            id(agent): agent for agent in agents}

    def add(self, agent: 'Agent'):
        self.agents_dic[id(agent)] = agent

    def remove(self, agent: 'Agent'):
        self.agents_dic.pop(id(agent))

    def get_all_agents(self) -> List['Agent']:
        return [agent for k, agent in self.agents_dic.items()]


class SortedAgentIndex:
    def __init__(self, agents: List['Agent'], standard: Callable[['Agent'], Union[int, float]]):
        self._agent_list: List[Tuple[Union[int, float], 'Agent']] = [(standard(agent), agent) for agent in agents]
        self._standard = standard
        self._agent_list.sort(key=lambda value_agent_tuple: value_agent_tuple[0])

    def add(self, agent: 'Agent'):
        index_list = self._agent_list
        val = self._standard(agent)
        index = binary_search(index_list, val)
        if index == -1:
            index_list.append((val, agent))
        else:
            index_list.insert(index, (val, agent))

    def remove(self, agent: 'Agent'):
        index_list = self._agent_list
        val = self._standard(agent)
        index = binary_search(index_list, val)
        index_list.pop(index)

    def update(self, agent: 'Agent', old_value: Union[int, float], new_value: Union[int, float]):
        index_list = self._agent_list
        pre_index = binary_search(index_list, old_value)
        index_list.pop(pre_index)
        after_index = binary_search(index_list, new_value)
        if after_index == -1:
            index_list.append((new_value, agent))
        else:
            index_list.insert(after_index, (new_value, agent))

    def __len__(self):
        return self._agent_list.__len__()

    def __getitem__(self, item):
        return self._agent_list[item][1]


class IndexedAgentList:
    """
    agent list with index.
    it could add/remove an agent at the complexity of O(1)
    """

    def __init__(self, agents: List['Agent']) -> None:
        self._index_dict: Dict[int, int] = {}  # stores the position map
        self._agent_list: List['Agent'] = []
        for i, agent in enumerate(agents):
            self._index_dict[id(agent)] = i
            self._agent_list.append(agent)

    def add(self, agent: "Agent"):
        index = len(self._agent_list)
        self._agent_list.append(agent)
        self._index_dict[id(agent)] = index

    def remove(self, agent: 'Agent'):
        index = self._index_dict.pop(id(agent))
        self._agent_list.pop(index)

    def get_all_agents(self):
        return self._agent_list

    def __repr__(self) -> str:
        return '<%s %s>' % (self.__class__.__name__, self._agent_list)

    def __len__(self) -> int:
        return len(self._agent_list)


class AgentGroup:
    def __init__(self, agents, standard: Callable[['Agent'], int]) -> None:
        self.groups: Dict[int, IndexedAgentList] = {}
        self.standard = standard
        for agent in agents:
            value = standard(agent)
            assert isinstance(value, int)
            if value not in self.groups:
                self.groups[value] = IndexedAgentList([agent])
            else:
                self.groups[value].add(agent)

    def update(self, agent, old: int, new: int):
        old_group = self.groups[old]

        old_group.remove(agent)
        new_group_val = new
        if new_group_val not in self.groups:
            self.groups[new_group_val] = IndexedAgentList([agent])

        else:
            self.groups[new_group_val].add(agent)

    def group_names(self) -> List[int]:
        return list(self.groups.keys())