from typing import ClassVar
from Melodie.agent import Agent

from Melodie.agent_manager import AgentManager


class Environment:
    def setup(self):
        pass
        # agent_class: ClassVar['Agent'], initial_agents: int
        # self.agent_manager = AgentManager(agent_class, initial_agents)
