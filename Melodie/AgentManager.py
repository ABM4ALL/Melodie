from typing import Dict, TYPE_CHECKING, ClassVar, List, Tuple
from .basic import AgentGroup, SortedAgentIndex

if TYPE_CHECKING:
    from .Agent import Agent


class AgentManager:
    def __init__(self, agent_class: ClassVar['Agent'], length: int) -> None:
        self.agent_class: ClassVar['Agent'] = agent_class
        self.initial_agent_num: int = length
        self.agents = self.setup_agents()

        self.indices: Dict[Tuple[str], SortedAgentIndex] = {
            k: SortedAgentIndex(self.agents, lambda agent: agent.val)
            for k in self.agents[0].indiced
        }

        self.groups: Dict[Tuple[str], AgentGroup] = {
            k: AgentGroup(
                self.agents, lambda agent: len(agent.text)
            )
            for k in self.agents[0].mapped
        }
        # l = [(agent.val, agent) for agent in self.agents]
        # l.sort(key=lambda o: o[0])
        # self.indices['val'] = l

    def __len__(self):
        return len(self.agents)

    def setup_agents(self) -> List['Agent']:
        agents = [self.agent_class(self) for a in range(self.initial_agent_num)]
        for agent in agents:
            agent.setup()

        agent = agents[0]
        for arg_names, func in agent.indiced.items():
            if not isinstance(arg_names, tuple):
                raise TypeError('Agent.indiced key type is expected to be Tuple[str,],'
                                f' like (\'aaaaa\',) or (\'bbbbb\',\'aaaa\'). But got type:{type(arg_names)},'
                                f'value: {arg_names}')
            for name in arg_names:
                if name not in agent._indiced_watch:
                    agent._indiced_watch[name] = (arg_names, [func])
                else:
                    agent._indiced_watch[name][1].append(func)

        for arg_names, func in agent.mapped.items():
            if not isinstance(arg_names, tuple):
                raise TypeError('Agent.mapped key type is expected to be Tuple[str,],'
                                f' like (\'aaaaa\',) or (\'bbbbb\',\'aaaa\'). But got type:{type(arg_names)},'
                                f'value: {arg_names}')
            for name in arg_names:
                if name not in agent._mapped_watch:
                    agent._mapped_watch[name] = (arg_names, [func])
                else:
                    agent._mapped_watch[name][1].append(func)

        agent.after_setup()
        for i in range(1, len(agents)):
            agents[i]._mapped_watch = agent._mapped_watch
            agents[i]._indiced_watch = agent._indiced_watch
            agent.after_setup()
        return agents

    def add_index(self):
        """
        add index to user defined properties
        :return:
        """
        pass

    def query(self):
        """
        How to implement this method?
        :return:
        """

