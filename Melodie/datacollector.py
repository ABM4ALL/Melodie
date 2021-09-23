from typing import List, ClassVar, TYPE_CHECKING

import pandas as pd

from Melodie.agent_manager import AgentManager
from Melodie.basic import MelodieExceptions
from Melodie.db import DB, create_db_conn

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
        from .run import get_environment, get_agent_manager, current_scenario
        env = get_environment()
        agent_manager = get_agent_manager()
        df_env = env.to_dataframe([prop.property_name for prop in self._environment_properties_to_collect])
        df_env['scenario_id'] = current_scenario().id
        df_env['step'] = step

        df_agent = agent_manager.to_dataframe([prop.property_name for prop in self._agent_properties_to_collect])
        df_agent['step'] = step
        df_agent['scenario_id'] = current_scenario().id

        self.agent_properties_df = pd.concat([self.agent_properties_df, df_agent], axis=0)

        self.environment_properties_df = pd.concat([self.environment_properties_df, df_env])

    def save(self):
        create_db_conn().write_dataframe(DB.AGENT_RESULT_TABLE, self.agent_properties_df)
        create_db_conn().write_dataframe(DB.ENVIRONMENT_RESULT_TABLE, self.environment_properties_df)
