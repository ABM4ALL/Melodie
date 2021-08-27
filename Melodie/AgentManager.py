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
            agent.after_setup()
        return agents

    def add_index(self):
        """
        add index to user defined properties
        :return:
        """
        pass
