from typing import List, ClassVar, TYPE_CHECKING

import pandas as pd

from Melodie.agent_manager import AgentManager
from Melodie.basic import MelodieExceptions
from Melodie.db import DB

if TYPE_CHECKING:
    from Melodie.agent import Agent


class PropertyToCollect:
    """
    It is property to collect.
    stores class and
    """

    def __init__(self, property_name: str, as_type: ClassVar):
        self.property_name = property_name
        self.as_type = as_type


class DataCollector:
    """
    Data Collector collects data for each scenario.
    At the beginning of simulation scenario, the DataCollector creates;
    User could customize when to dump data to dataframe.
    By simulation scenario exits, the DataCollector dumps the data to dataframe, and save to
    database or datafile.
    """

    def __init__(self, target='sqlite'):
        assert target in {'sqlite'}
        self.target = target
        self._agent_properties_to_collect: List[PropertyToCollect] = []
        self._environment_properties_to_collect: List[PropertyToCollect] = []

        self.agent_properties_df = pd.DataFrame()
        self.environment_properties_df = pd.DataFrame()
        self.setup()

    def setup(self):
        pass

    def add_agent_property(self, property_name: str, as_type: ClassVar = None):
        self._agent_properties_to_collect.append(PropertyToCollect(property_name, as_type))

    def add_environment_property(self, property_name: str, as_type: ClassVar = None):
        self._environment_properties_to_collect.append(PropertyToCollect(property_name, as_type))

    def collect(self, step: int):
        from .run import get_environment, get_agent_manager
        env = get_environment()
        agent_manager = get_agent_manager()
        env_dict = {}
        for k, v in env.__dict__.items():
            if k in self._environment_properties_to_collect:
                env_dict[k] = v
        df = agent_manager.to_dataframe([prop.property_name for prop in self._agent_properties_to_collect])
        df['step'] = step
        # print(self._environment_properties_to_collect, self._agent_properties_to_collect)
        # print('env', env.to_json())
        # print('agents', df)
        self.agent_properties_df = pd.concat([self.agent_properties_df, df], axis=0)

    def save(self, proj_name: str):
        DB(proj_name).write_dataframe('agent_results', self.agent_properties_df)

    def store_data(self, env_data: dict, agents_data: pd.DataFrame):
        """
        The method to store data into dataframe.
        :param env_data:
        :param agents_data:
        :return:
        """
        if self.target in {'sqlite'}:
            db = DB()
            db.write_dataframe('agent_data', agent)
        elif self.target in {'csv', 'json'}:
            raise NotImplementedError
