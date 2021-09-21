from typing import Tuple

from Melodie.agent_manager import AgentManager
from Melodie.basic import MelodieExceptions


class Environment:
    def setup(self):
        pass
        # agent_class: ClassVar['Agent'], initial_agents: int
        # self.agent_manager = AgentManager(agent_class, initial_agents)

    # def get_agent_manager(self) -> Tuple[str, AgentManager]:
    #     return self.agent_manager

    def to_json(self, ):
        pass
