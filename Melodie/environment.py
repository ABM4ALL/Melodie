from typing import Tuple, List

import pandas as pd

from Melodie.agent_manager import AgentManager
from Melodie.basic import MelodieExceptions


class Environment:
    def setup(self):
        pass
        # agent_class: ClassVar['Agent'], initial_agents: int
        # self.agent_manager = AgentManager(agent_class, initial_agents)

    # def get_agent_manager(self) -> Tuple[str, AgentManager]:
    #     return self.agent_manager

    def to_dataframe(self, properties: List[str]):
        """
        Dump Environment to a one-row pd.DataFrame
        :param properties:
        :return:
        """
        if properties is None:
            properties = self.__dict__.keys()
        d = {}
        for property in properties:
            d[property] = self.__dict__[property]
        return pd.DataFrame([d])
