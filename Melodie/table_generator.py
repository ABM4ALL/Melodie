# -*- coding:utf-8 -*-
# @Time: 2021/9/21 10:45
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: table_generator.py

# -*- coding: utf-8 -*-
__author__ = 'Songmin'

import logging
from typing import Callable, Any, Union

import pandas as pd

from Melodie.db import create_db_conn
from Melodie.scenariomanager import Scenario

logger = logging.getLogger(__name__)


class TableGenerator:

    def __init__(self, scenario: 'Scenario'):
        """
        Pass the class of agent, to get the data type that how the properties are saved into database.
        :param conn:
        :param scenario:
        :param agentClass:
        """

        self.scenario = scenario
        self._agent_params = []
        self._environment_params = []

    def parse_generator(self, generator) -> Callable[[], Any]:
        if callable(generator):
            if generator.__code__.co_argcount == 0:
                return lambda x: generator()
            elif generator.__code__.co_argcount == 1:
                return generator
        elif isinstance(generator, (int, float, str)):
            return lambda x: generator
        else:
            raise TypeError(generator)

    def add_agent_param(self, param_name, generator: Union[int, str, float, Callable[[int], Any]]):
        """
        Add parameters to assign to agent properties.
        Generator is a function
        :param param_name:
        :param generator:
        :return:
        """
        self._agent_params.append((param_name, self.parse_generator(generator)))

    def add_environment_param(self, param_name, generator: Union[int, str, float, Callable[[int], Any]]):
        self._environment_params.append((param_name, self.parse_generator(generator)))

    @property
    def agent_params(self):
        return self._agent_params

    def gen_agent_param_table(self):
        agent_num = self.scenario.agent_num
        data_list = []
        for agent_id in range(0, agent_num):
            d = {}
            d['scenario_id'] = self.scenario.id
            d['id'] = agent_id
            d.update({k: g(agent_id) for k, g in self._agent_params})

            data_list.append(d)

        return pd.DataFrame(data_list)

    def gen_environment_param_table(self):
        d = {'scenario_id': self.scenario.id}
        d.update({k: g() for k, g in self._environment_params})

    def run(self):
        from Melodie.run import get_config
        df = self.gen_agent_param_table()
        config = get_config()
        if config.with_db:
            db_conn = create_db_conn()
            db_conn.write_dataframe(db_conn.AGENT_PARAM_TABLE, df)
        return df

    def setup(self):
        pass
