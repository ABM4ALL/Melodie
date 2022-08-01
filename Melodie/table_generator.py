# -*- coding:utf-8 -*-

import logging
from typing import Callable, Union, TYPE_CHECKING, Optional

import pandas as pd

from .basic import MelodieExceptions, args_check
from .scenario_manager import Scenario

if TYPE_CHECKING:
    from .dataframe_loader import DataFrameLoader

logger = logging.getLogger(__name__)


class TableGenerator:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        new_df = self.gen_agent_param_table_each_scenario()
        self.df_loader.register_dataframe(self.table_name, new_df, self.data_types)
        return

    def __init__(
            self,
            df_loader: "DataFrameLoader",
            table_name: str,
            num_generator: Union[int, Callable[[Scenario], int]],
    ):
        """
        :param df_loader:
        :param table_name:
        """

        self.num_generator = self.convert_to_num_generator(num_generator)
        self.table_name = table_name
        self._self_incremental_value = -1
        self.df_loader = df_loader
        from Melodie.dataframe_loader import DataFrameLoader

        if not isinstance(self.df_loader, DataFrameLoader):
            MelodieExceptions.Data.NoDataframeLoaderDefined()

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
        if len(self.data_types) > 0:
            raise ValueError("Data types has been already defined!")
        self.data_types = data_types

    def convert_to_num_generator(
            self, num_generator: Union[int, Callable[[Scenario], int]]
    ):
        if isinstance(num_generator, int):
            return lambda _: num_generator
        elif callable(num_generator):
            args_check(num_generator, 1)
            return num_generator
        else:
            raise TypeError

    def set_row_generator(
            self, row_generator: Callable[[Scenario], Union[dict, object]]
    ):
        """
        Set the geneator for each row. Every time the row_generator is called, this function
        returns a dict standing for one row.
        For example, if row_generator is called twice, and the return values are {"id": 0, "a": 1},
            and {"id": 1, "a": 2}. The generated table will be:
        | id | a |
        |----|---|
        | 0  | 1 |
        | 1  | 2 |

        :param row_generator:
        :return:
        """
        args_check(row_generator, 1)
        self._row_generator = row_generator

    def gen_agent_param_table_each_scenario(self):
        """

        :return:
        """
        scenarios = self.df_loader.manager.generate_scenarios()
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
            d = {"scenario_id": scenario.id, "id": agent_id}
            generated = self._row_generator(scenario)
            if isinstance(generated, dict):
                d.update(generated)
            elif not type(generated).__module__ == "__builtin__":
                d.update(generated.__dict__)
            else:
                raise TypeError(
                    f"Builtin type {type(generated)} (value: {generated}) cannot be converted to table row."
                )
            data_list.append(d)
        return data_list
