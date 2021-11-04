from typing import Tuple, List, Dict, Optional, TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from Melodie import Model


class Environment:
    def __init__(self):
        self.model: Optional['Model'] = None

    def current_scenario(self):
        assert self.model.scenario is not None
        return self.model.scenario

    def setup(self):
        pass
        # agent_class: ClassVar['Agent'], initial_agents: int
        # self.agent_manager = AgentList(agent_class, initial_agents)

    # def get_agent_manager(self) -> Tuple[str, AgentList]:
    #     return self.agent_manager

    def to_dict(self, properties: List[str]) -> Dict:
        if properties is None:
            properties = self.__dict__.keys()
        d = {}
        for property in properties:
            d[property] = self.__dict__[property]
        return d

    def to_dataframe(self, properties: List[str]):
        """
        Dump Environment to a one-row pd.DataFrame
        :param properties:
        :return:
        """
        d = self.to_dict(properties)
        return pd.DataFrame([d])
