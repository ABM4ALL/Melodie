# -*- coding:utf-8 -*-
# @Time: 2021/9/21 10:45
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: table_generator.py

# -*- coding: utf-8 -*-
__author__ = 'Songmin'

import logging
import random
from typing import Callable, Any, Union, Tuple, List

import pandas as pd

from Melodie.db import create_db_conn
from Melodie.scenario_manager import Scenario

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
        self._agent_params: List[Tuple[str, Callable]] = []
        self._environment_params: List[Tuple[str, Callable]] = []

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
        logger.warning('<Developer Notice>: Table generator needs to be called before model created.')
        self._agent_params.append((param_name, self.parse_generator(generator)))

    def add_environment_param(self, param_name, generator: Union[int, str, float, Callable[[int], Any]]):
        """
        Add parameters to assign to environment properties.
        Generator is a function
        :param param_name:
        :param generator:
        :return:
        """
        logger.warning('<Developer Notice>: Table generator needs to be called before model created.')
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

    def set_agent_params(self):
        # TODO: 这种方法可能也不够通用
        # TODO: 有没有更好的方法？
        # TODO: 更复杂的情况可以使用读取表的方法。举例：每个企业的技术水平不一样，生产规模不一样。这种需要读excel表。
        a = random.randint()
        b = a ** 2
        return {'a': a, 'b': b}

    def read_param_table(self):
        """
        TODO
        做一个判断。
        如果用scenario里面的一行，里面要么是和环境有关的参数，要么是和Agent有关的参数。
        TODO 优先做这个:从Excel读取环境数据的时候，不用跑table generator.

        含有一个名为scenarios的表，保存所有的scenario
        每一个scenario的agent table分开，分为多个工作表。 工作表名称和scenario_id一样。

        最好也生成一个环境的参数表、

        准备Agent的参数时，有两种方案。
        - 第一种使用set_agent_params自动生成
        - 第二种是直接读进来完整的agent表。表名可以做一个区分。
             1、scenarios表+所有scenarios的表。
             2、只有一个Agent参数表，那么所有的情况都用同样的agent参数
        环境参数表，表名为environment_parameter。
        保存的是对应scenario中的环境参数。

        giniscenario表
        :return:
        """
