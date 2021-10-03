import time
from typing import List, ClassVar, TYPE_CHECKING

import pandas as pd
import logging
from Melodie.db import DB, create_db_conn

logger = logging.getLogger(__name__)

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
        assert target in {'sqlite', None}
        self.target = target
        self._agent_properties_to_collect: List[PropertyToCollect] = []
        self._environment_properties_to_collect: List[PropertyToCollect] = []

        self.agent_properties_df = pd.DataFrame()
        self.environment_properties_df = pd.DataFrame()

        self.agent_properties_list = []
        self.environment_properties_list = []
        self.setup()

        self._time_elapsed = 0

    def setup(self):
        pass

    def add_agent_property(self, property_name: str, as_type: ClassVar = None):
        self._agent_properties_to_collect.append(PropertyToCollect(property_name, as_type))

    def add_environment_property(self, property_name: str, as_type: ClassVar = None):
        self._environment_properties_to_collect.append(PropertyToCollect(property_name, as_type))

    def env_property_names(self):
        return [prop.property_name for prop in self._environment_properties_to_collect]

    def agent_property_names(self):
        return [prop.property_name for prop in self._agent_properties_to_collect]

    def collect(self, step: int):
        t0 = time.time()
        from .run import get_environment, get_agent_manager, current_scenario, get_run_id
        env = get_environment()
        agent_manager = get_agent_manager()
        run_id = get_run_id()
        env_dic = env.to_dict(self.env_property_names())
        env_dic['step'] = step
        env_dic['scenario_id'] = current_scenario().id
        env_dic['run_id'] = run_id

        agent_prop_list = agent_manager.to_list(self.agent_property_names())
        for agent_prop in agent_prop_list:
            agent_prop['step'] = step
            agent_prop['run_id'] = run_id
            agent_prop['scenario_id'] = current_scenario().id

        self.agent_properties_list.extend(agent_prop_list)
        self.environment_properties_list.append(env_dic)

        t1 = time.time()
        self._time_elapsed += (t1 - t0)

    def save(self):
        t0 = time.time()
        self.agent_properties_df = pd.DataFrame(self.agent_properties_list)
        self.environment_properties_df = pd.DataFrame(self.environment_properties_list)

        # create_db_conn().batch_insert(DB.AGENT_RESULT_TABLE, self.agent_properties_list)
        # create_db_conn().batch_insert(DB.ENVIRONMENT_RESULT_TABLE, self.environment_properties_list)

        create_db_conn().write_dataframe(DB.AGENT_RESULT_TABLE, self.agent_properties_df)
        create_db_conn().write_dataframe(DB.ENVIRONMENT_RESULT_TABLE, self.environment_properties_df)
        t1 = time.time()
        self._time_elapsed += time.time() - t0
        logger.info(f'datacollector took {t1 - t0}s to format dataframe and write it to database.')
