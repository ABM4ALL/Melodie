from typing import Dict, TYPE_CHECKING, ClassVar, List, Tuple, Callable, Union
from .basic import AgentGroup, SortedAgentIndex, parse_watched_attrs, IndexedAgentList

if TYPE_CHECKING:
    from .agent import Agent


class AgentManager:
    def __init__(self, agent_class: ClassVar['Agent'], length: int) -> None:
        self.agent_class: ClassVar['Agent'] = agent_class
        self.initial_agent_num: int = length
        self.agents = self.setup_agents()

        self.setup()

    def __len__(self):
        return len(self.agents)

    def setup(self):
        pass

    def setup_agents(self) -> IndexedAgentList:
        agents = [self.agent_class() for _ in range(self.initial_agent_num)]
        for agent in agents:
            agent.setup()
        return IndexedAgentList(agents)

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


