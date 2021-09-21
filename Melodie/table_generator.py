# -*- coding:utf-8 -*-
# @Time: 2021/9/21 10:45
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: table_generator.py

# -*- coding: utf-8 -*-
__author__ = 'Songmin'

import logging
from typing import ClassVar, Callable, Any, Union

import numpy as np
import pandas as pd
import pandas.io.sql

from Melodie.config import CONN
from Melodie.db import DB
from Melodie.agent import Agent
from Melodie.scenariomanager import Scenario

logger = logging.getLogger(__name__)


class TableGenerator:

    def __init__(self, db_name, scenario: 'Scenario'):
        """
        Pass the class of agent, to get the data type that how the properties are saved into database.
        :param conn:
        :param scenario:
        :param agentClass:
        """
        # 5 tables in database
        # scenarios, agent_params, env_params, agent_results, env_results
        # self.db = DB(db_name)
        self.db_name = db_name
        self.scenario = scenario
        self._agent_params = []
        self._environment_params = []
        # try:
        #     db.read_dataframe('agent_params')  # , self.Conn, ID_Scenario=self.Scenario.ID_Scenario).iloc[0]
        # except pandas.io.sql.DatabaseError:
        #     logger.warning(
        #         f"Table {'agent_params'} does not exist and it will be created storing default value")
        #     db.create_scenario(self.Scenario)

    def parse_generator(self, generator) -> Callable[[], Any]:
        if callable(generator):
            assert generator.__code__.co_argcount == 0
            return generator
        elif isinstance(generator, (int, float, str)):
            return lambda: generator
        else:
            raise TypeError(generator)

    def add_agent_param(self, param_name, generator: Union[int, str, float, Callable[[], Any]]):
        self._agent_params.append((param_name, self.parse_generator(generator)))

    def add_environment_param(self, param_name, generator: Union[int, str, float, Callable[[], Any]]):
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
            d.update({k: g() for k, g in self._agent_params})

            data_list.append(d)
        # print(data_list)
        df = pd.DataFrame(data_list)
        DB(self.db_name).write_dataframe('agent_params', df)
        df2 = DB(self.db_name).read_dataframe('agent_params')
        # print(df2)
        # data_column = self.agentClass.types
        # # DB().write_DataFrame(agentParaTable, REG().Gen_AgentPara + "_S" + str(self.Scenario.ID_Scenario),
        # #                      data_column.keys(), self.Conn, dtype=data_column)
        # agent_params = pd.DataFrame(agentParaTable, columns=data_column.keys())
        # DB('WealthDistribution').write_dataframe(REG().Gen_AgentPara + "_S" + str(self.Scenario.ID_Scenario),
        #                                          agent_params)
        # data_column.keys(), self.Conn, dtype=data_column)

    def run(self):
        self.gen_agent_param_table()

    def setup(self):
        pass
