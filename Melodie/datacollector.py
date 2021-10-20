import csv
import io
import json
import mmap
import os.path
import pickle
import time
from typing import List, ClassVar, TYPE_CHECKING

import pandas as pd
import logging

from Melodie.db import DB

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from Melodie.agent import Agent
    from Melodie import Model


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
    data or datafile.
    """

    def __init__(self, model: 'Model', target='sqlite'):
        assert target in {'sqlite', None}
        self.target = target
        self.model = model
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
        env = self.model.environment
        agent_manager = self.model.agent_manager
        scenario = self.model.current_scenario()
        run_id = self.model.run_id_in_scenario
        env_dic = env.to_dict(self.env_property_names())
        env_dic['step'] = step
        env_dic['scenario_id'] = scenario.id
        env_dic['run_id'] = run_id

        agent_prop_list = agent_manager.to_list(self.agent_property_names())
        for agent_prop in agent_prop_list:
            agent_prop['step'] = step
            agent_prop['run_id'] = run_id
            agent_prop['scenario_id'] = scenario.id

        self.agent_properties_list.extend(agent_prop_list)
        self.environment_properties_list.append(env_dic)

        t1 = time.time()
        self._time_elapsed += (t1 - t0)

    def save(self):
        t0 = time.time()
        # for item in self.agent_properties_list:
        #     str(item)
        #     pass
        # info =
        # with open('test4.csv', 'w',buffering=1000) as csvfile:
        #     pass
        # with io.StringIO() as csvfile:
        #     json.dumps(self.agent_properties_list)
        #     writer = csv.DictWriter(csvfile, fieldnames=['step', 'run_id', 'scenario_id','id'] + self.agent_property_names())
        #     writer.writeheader()
        #     writer.writerows(self.agent_properties_list)
        # pickle.dumps(self.agent_properties_list)
        # json.dumps(self.agent_properties_list)

        pid = os.getpid()
        #
        self.agent_properties_df = pd.DataFrame(self.agent_properties_list)
        self.environment_properties_df = pd.DataFrame(self.environment_properties_list)
        if os.path.exists(f'temp/a_{pid}.csv'):
            self.agent_properties_df.to_csv(f'temp/a_{pid}.csv', mode='a', header=False)
            self.environment_properties_df.to_csv(f'temp/e_{pid}.csv', mode='a', header=False)
        else:
            self.agent_properties_df.to_csv(f'temp/a_{pid}.csv', mode='w', header=True)
            self.environment_properties_df.to_csv(f'temp/e_{pid}.csv', mode='w', header=True)

        # self.agent_properties_df.to_feather('p.feather')

        # self.agent_properties_df = pd.DataFrame(self.agent_properties_list)
        # self.environment_properties_df = pd.DataFrame(self.environment_properties_list)
        # self.model.create_db_conn()#.write_dataframe(DB.AGENT_RESULT_TABLE, self.agent_properties_df)
        # self.model.create_db_conn()#.write_dataframe(DB.ENVIRONMENT_RESULT_TABLE, self.environment_properties_df)

        # with open('agent.pkl', 'wb', buffering=4096) as f:
        #     # mm = mmap.mmap(f.fileno(), 4096)
        #
        #     pickle.dump(self.agent_properties_list, f)
        #
        # with open('env.pkl', 'wb', buffering=4096) as f:
        #     pickle.dump(self.environment_properties_list, f)
        # self.agent_properties_df.to_pickle('agent.csv')
        # self.environment_properties_df.to_pickle('env.csv')
        # self.model.create_db_conn().batch_insert(DB.AGENT_RESULT_TABLE, self.agent_properties_list)
        # self.model.create_db_conn().batch_insert(DB.ENVIRONMENT_RESULT_TABLE, self.environment_properties_list)

        t1 = time.time()
        collect_time = self._time_elapsed
        db_wrote_time = t1 - t0
        self._time_elapsed += db_wrote_time
        logger.info(f'datacollector took {t1 - t0}s to format dataframe and write it to data.\n'
                    f'    {db_wrote_time} for writing into database, and {collect_time} for collect data.')
