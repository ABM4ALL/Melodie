from typing import Dict, TYPE_CHECKING, ClassVar, List, Tuple, Callable, Union
from .basic import AgentGroup, SortedAgentIndex, parse_watched_attrs, IndexedAgentList

if TYPE_CHECKING:
    from .Agent import Agent


class AgentManager:
    def __init__(self, agent_class: ClassVar['Agent'], length: int) -> None:
        self.agent_class: ClassVar['Agent'] = agent_class
        self.initial_agent_num: int = length
        self.agents = self.setup_agents()

        self.sorted_indices: Dict[str, Callable] = {}
        self.grouped_indices: Dict[str, Callable] = {}

        # map single attribute name to functions list.
        self.sorted_watch: Dict[str, Tuple[Tuple, List[Callable]]] = {}
        self.grouped_watch: Dict[str, Tuple[Tuple, List[Callable]]] = {}

        self.indices: Dict[Tuple[str], SortedAgentIndex] = {}

        self.groups: Dict[Tuple[str], AgentGroup] = {}

        self.indices_dict: Dict[str, Union[AgentGroup, SortedAgentIndex]] = {}
        self.setup()
        self.setup_indices()

    def __len__(self):
        return len(self.agents)

    def setup(self):
        pass

    def setup_agents(self) -> IndexedAgentList:
        agents = [self.agent_class(self) for _ in range(self.initial_agent_num)]
        for agent in agents:
            agent.setup()
        return IndexedAgentList(agents)

    def setup_indices(self):
        agents = self.agents
        for name, func in self.sorted_indices.items():
            arg_names = tuple(parse_watched_attrs(func))
            if not isinstance(arg_names, tuple):
                raise TypeError('Agent.indiced key type is expected to be Tuple[str,],'
                                f' like (\'aaaaa\',) or (\'bbbbb\',\'aaaa\'). But got type:{type(arg_names)},'
                                f'value: {arg_names}')
            self.indices[arg_names] = SortedAgentIndex(self.agents, func)
            self.indices_dict[name] = self.indices[arg_names]
            for arg_name in arg_names:
                if arg_name not in self.sorted_watch:
                    self.sorted_watch[arg_name] = (arg_names, [func])
                else:
                    self.sorted_watch[arg_name][1].append(func)

        for name, func in self.grouped_indices.items():
            arg_names = tuple(parse_watched_attrs(func))
            if not isinstance(arg_names, tuple):
                raise TypeError('Agent.mapped key type is expected to be Tuple[str,],'
                                f' like (\'aaaaa\',) or (\'bbbbb\',\'aaaa\'). But got type:{type(arg_names)},'
                                f'value: {arg_names}')
            self.groups[arg_names] = AgentGroup(self.agents, func)
            self.indices_dict[name] = self.groups[arg_names]
            for arg_name in arg_names:
                if arg_name not in self.grouped_watch:
                    self.grouped_watch[arg_name] = (arg_names, [func])
                else:
                    self.grouped_watch[arg_name][1].append(func)

        for i in range(len(agents)):
            agents[i]._mapped_watch = self.grouped_watch
            agents[i]._indiced_watch = self.sorted_watch
            agents[i].after_setup()

    def add_sorted_index(self, index_name: str, ):
        """
        add index to user defined properties
        :return:
        """

    def add_grouped_index(self, index_name: str):
        """

        :param index_name:
        :return:
        """

    def query(self):
        """
        How to implement this method?
        :return:
        """

    def remove(self, agent: 'Agent'):
        for i, a in enumerate(self.agents):
            if a is agent:
                self.agents.pop(i)
                break
        for name, index in self.indices_dict.items():
            self.indices_dict[name].remove(agent)

    def add(self, agent: 'Agent'):
        self.agents.add(agent)

        for name, index in self.indices_dict.items():
            self.indices_dict[name].add(agent)
