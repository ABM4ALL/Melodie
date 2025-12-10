# -*- coding:utf-8 -*-

import logging
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Union

from sqlalchemy import Float, Integer

from MelodieInfra import GeneralTable, MelodieExceptions, Table

from .scenario_manager import Scenario
from .utils import args_check

if TYPE_CHECKING:
    from .data_loader import DataFrameInfo, DataLoader

logger = logging.getLogger(__name__)


class DataFrameGenerator:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        new_df = self.gen_agent_param_table_each_scenario()
        self.df_loader.register_dataframe(
            self.df_info.df_name, new_df, self.df_info.columns
        )

    def __init__(
        self,
        df_loader: "DataLoader",
        df_info: "DataFrameInfo",
        num_generator: Union[int, Callable[[Scenario], int]],
    ):
        """
        :param df_loader: The ``DataLoader`` instance.
        :param df_info: The ``DataFrameInfo`` describing the table to generate.
        :param num_generator: An integer for a fixed number of rows per scenario,
            or a callable that takes a ``Scenario`` object and returns the
            number of rows to generate.
        """

        self.num_generator = self.convert_to_num_generator(num_generator)
        self.df_info = df_info
        self._self_incremental_value = -1
        self.df_loader = df_loader
        from Melodie.data_loader import DataLoader

        if not isinstance(self.df_loader, DataLoader):
            MelodieExceptions.Data.NoDataframeLoaderDefined()

        self._row_generator: Optional[Callable[[Scenario], Union[dict, object]]] = None

    def increment(self):
        """
        Get a new, auto-incrementing integer value, starting from 0.

        This is useful for generating unique IDs within a scenario's rows. The
        counter is automatically reset for each new scenario.
        """
        self._self_incremental_value += 1
        return self._self_incremental_value

    def reset_increment(self):
        """
        Reset the auto-incrementing counter to -1.
        """
        self._self_incremental_value = -1

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
        self, row_generator: Callable[[Union[Any, Scenario]], Union[Dict[str, Any]]]
    ):
        """
        Set the function that generates the data for a single row.

        The provided callable will be executed for each row to be generated. It
        should take the current ``Scenario`` object as its argument and return a
        dictionary representing the data for one row.

        Example:
            If ``row_generator`` is called twice and returns ``{"id": 0, "a": 1}``
            and ``{"id": 1, "a": 2}``, the generated table will contain these two
            rows.

        :param row_generator: A callable that takes a ``Scenario`` and returns a
            dictionary.
        """
        args_check(row_generator, 1)
        self._row_generator = row_generator

    def gen_agent_param_table_each_scenario(self):
        """
        (Internal) Generate the full table by iterating through all scenarios.
        """
        scenarios = self.df_loader.manager.generate_scenarios()
        data_list = []
        for scenario in scenarios:
            data_list.extend(self.gen_agent_params(scenario))
            self.reset_increment()
        assert len(data_list) > 0, "Agent param table should contain more than one row"
        cols = {
            k: Integer() if isinstance(v, int) else Float()
            for k, v in data_list[0].items()
        }
        return GeneralTable.from_dicts(cols, data_list)

    def gen_agent_params(self, scenario: Scenario):
        """
        (Internal) Generate the rows for a single scenario.
        """
        data_list = []
        for agent_id in range(0, self.num_generator(scenario)):
            d = {"id_scenario": scenario.id, "id": agent_id}
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
