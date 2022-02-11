
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
from typing import ClassVar

from .config import Config
from .db import create_db_conn, DB
from .plotter import Plotter

class Analyzer(ABC):

    def __init__(self, config: Config, plotter_cls: ClassVar[Plotter] = Plotter):
        self.config = config
        self.plotter = plotter_cls(config)
        self.setup()
        self.conn = self.create_db_conn(config)

    @abstractmethod
    def setup(self):
        pass

    def create_db_conn(self, config) -> 'DB':
        return create_db_conn(config)

    def _check_if_df_loaded(self, df_name: str):
        loaded_df_name = "loaded_" + df_name
        if loaded_df_name in self.__dict__.keys():
            return True
        else:
            return False

    def read_dataframe(self, df_name: str):
        loaded_df_name = "loaded_" + df_name
        if self._check_if_df_loaded(df_name):
            df = self.__dict__[loaded_df_name]
        else:
            df = self.conn.read_dataframe(df_name)
            self.__setattr__(loaded_df_name, df)
        return df

    def filter_dataframe(self, df: pd.DataFrame, filter: dict):
        df_filtered = df.loc[(df[list(filter)] == pd.Series(filter)).all(axis=1)]
        return df_filtered

    def plot_trainer_agent_strategy_params_cov_heatmap(self,
                                                       strategy_params_list: list,
                                                       df: pd.DataFrame,
                                                       trainer_scenario_id: int,
                                                       generation_id: int,
                                                       trainer_params_scenario_id: int = 0,
                                                       path_id: int = 0,
                                                       strategy_params_ticks: list = None):
        filter = {"trainer_scenario_id": trainer_scenario_id,
                  "trainer_params_scenario_id": trainer_params_scenario_id,
                  "path_id": path_id,
                  "generation_id": generation_id}
        df_filtered = self.filter_dataframe(df, filter)
        df_filtered = df_filtered.fillna(0)
        agent_num = len(df_filtered)
        params_num = len(strategy_params_list)
        cov_matrix = np.zeros((params_num, agent_num))
        for param_id in range(0, len(strategy_params_list)):
            column_name = strategy_params_list[param_id] + "_cov"
            param_cov = df_filtered[column_name].to_numpy()
            cov_matrix[param_id,:] = param_cov
        fig_scenario = "_TS" + str(trainer_scenario_id) + "TPS" + str(trainer_params_scenario_id) + \
                       "P" + str(path_id) + "G" + str(generation_id) + "_"
        self.plotter.trainer_agent_strategy_params_cov_heatmap(cov_matrix, fig_scenario,
                                                               strategy_params_ticks=strategy_params_ticks)

    def plot_trainer_agent_var_scatter(self,
                                       var_1_name: str,
                                       var_2_name: str,
                                       df: pd.DataFrame,
                                       trainer_scenario_id: int,
                                       generation_id: int,
                                       trainer_params_scenario_id: int = 0,
                                       path_id: int = 0,
                                       area_value: np.array = None,
                                       var_1_lim=None, var_2_lim=None,
                                       var_1_label=None, var_2_label=None,
                                       fig_title=None):
        filter = {"trainer_scenario_id": trainer_scenario_id,
                  "trainer_params_scenario_id": trainer_params_scenario_id,
                  "path_id": path_id,
                  "generation_id": generation_id}
        df_filtered = self.filter_dataframe(df, filter)
        var_1_value = df_filtered[var_1_name].to_numpy()
        var_2_value = df_filtered[var_2_name].to_numpy()
        fig_scenario = "_TS" + str(trainer_scenario_id) + "TPS" + str(trainer_params_scenario_id) + \
                       "P" + str(path_id) + "G" + str(generation_id) + "_"
        self.plotter.trainer_agent_var_scatter(var_1_name, var_1_value,
                                               var_2_name, var_2_value,
                                               fig_scenario,
                                               area_value=area_value,
                                               var_1_lim=var_1_lim, var_2_lim=var_2_lim,
                                               var_1_label=var_1_label, var_2_label=var_2_label,
                                               fig_title=fig_title)

    def plot_trainer_env_var(self,
                             var_name: str,
                             df: pd.DataFrame,
                             trainer_scenario_id: int,
                             trainer_params_scenario_id: int = 0,
                             path_id: int = None,
                             fig_title=None,
                             y_label=None,
                             y_lim=None):
        filter = {"trainer_scenario_id": trainer_scenario_id,
                  "trainer_params_scenario_id": trainer_params_scenario_id}
        if path_id != None: filter["path_id"] = path_id
        df_filtered = self.filter_dataframe(df, filter)

        var_mean_name = var_name + "_mean"
        var_cov_name = var_name + "_cov"
        var_value_dict = {}
        path_id_set = set(df_filtered["path_id"])
        for path_id in path_id_set:
            key = "path_" + str(path_id)
            df_filtered_path_id = df_filtered.loc[df_filtered["path_id"] == path_id]
            var_value_dict[key] = [df_filtered_path_id[var_mean_name].to_numpy(),
                                   df_filtered_path_id[var_cov_name].to_numpy()]
        fig_scenario = "_TS" + str(trainer_scenario_id) + "TPS" + str(trainer_params_scenario_id) + "_"
        self.plotter.trainer_env_var(var_name, var_value_dict, fig_scenario,
                                     fig_title=fig_title, y_label=y_label, y_lim=y_lim)










