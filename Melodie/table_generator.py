# -*- coding:utf-8 -*-
# @Time: 2021/9/21 10:45
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: table_generator.py

import logging
import random
from typing import Callable, Any, Union, Tuple, List, TYPE_CHECKING, Optional

import pandas as pd

from Melodie.db import create_db_conn
from Melodie.scenario_manager import Scenario

if TYPE_CHECKING:
    from Melodie import Simulator

logger = logging.getLogger(__name__)


class TableGenerator:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        new_df = self.gen_agent_param_table_each_scenario()
        self.simulator.register_dataframe(self.table_name, new_df, self.data_types)
        return

    def __init__(self, simulator: "Simulator", table_name: str, num_generator: Union[int, Callable[[Scenario], int]]):
        """

        :param table_name:
        """

        self.num_generator = self.convert_to_num_generator(num_generator)
        self.table_name = table_name
        self._self_incremental_value = -1
        self.simulator = simulator
        self.data_types = {}
        self._row_generator: Optional[Callable[[Scenario], Union[dict, object]]] = None

    def increment(self):
        """
        Get increment value.
        :return:
        """
        self._self_incremental_value += 1
        return self._self_incremental_value

    def reset_increment(self):
        """
        Reset increment
        :return:
        """
        self._self_incremental_value = -1

    def set_column_data_types(self, data_types: dict):
        """
        Set data types of each column
        :param data_types:
        :return:
        """
        assert len(self.data_types) == 0, "Data types has been already defined!"
        self.data_types = data_types

    def convert_to_num_generator(self, num_generator: Union[int, Callable[[Scenario], int]]):
        if isinstance(num_generator, int):
            return lambda _: num_generator
        elif callable(num_generator):
            assert num_generator.__code__.co_argcount == 1
            return num_generator
        else:
            raise TypeError

    def set_row_generator(self, row_generator: Callable[[Scenario], Union[dict, object]]):
        """

        :param row_generator:
        :return:
        """
        assert row_generator.__code__.co_argcount == 1
        self._row_generator = row_generator

    def gen_agent_param_table_each_scenario(self):
        """

        :return:
        """
        scenarios = self.simulator.generate_scenarios()
        data_list = []
        for scenario in scenarios:
            data_list.extend(self.gen_agent_params(scenario))
            self.reset_increment()
        return pd.DataFrame(data_list)

    def gen_agent_params(self, scenario: Scenario):
        """

        :param scenario:
        :return:
        """
        data_list = []
        for agent_id in range(0, self.num_generator(scenario)):
            d = {}
            d['scenario_id'] = scenario.id
            d['id'] = agent_id
            generated = self._row_generator(scenario)
            if isinstance(generated, dict):
                d.update(generated)
            elif not type(generated).__module__ == "__builtin__":
                d.update(generated.__dict__)
            else:
                raise TypeError(
                    f"Builtin type {type(generated)} (value: {generated}) cannot be converted to table row.")
            data_list.append(d)
        return data_list


