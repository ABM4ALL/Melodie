
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
from typing import ClassVar, Dict

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
        fig_scenario = "TS" + str(trainer_scenario_id) + "TPS" + str(trainer_params_scenario_id) + \
                       "P" + str(path_id) + "G" + str(generation_id)
        self.plotter.trainer_agent_strategy_params_cov_heatmap(cov_matrix, fig_scenario,
                                                               strategy_params_ticks=strategy_params_ticks)

    def plot_trainer_agent_strategy_params_cov_lines(self,
                                                     strategy_params_list: list,
                                                     df: pd.DataFrame,
                                                     trainer_scenario_id: int,
                                                     trainer_params_scenario_id: int = 0,
                                                     path_id: int = 0,
                                                     strategy_params_legend_dict: dict = None):
        filter = {"trainer_scenario_id": trainer_scenario_id,
                  "trainer_params_scenario_id": trainer_params_scenario_id,
                  "path_id": path_id}
        df_filtered = self.filter_dataframe(df, filter)
        df_filtered = df_filtered.fillna(0)
        generation_num = len(df_filtered.loc[df_filtered["agent_id"] == 0])
        agent_num = len(df_filtered.loc[df_filtered["generation_id"] == 0])
        strategy_params_agent_generation_matrix_dict: Dict[str, np.ndarray] = {}
        for param_id in range(0, len(strategy_params_list)):
            agent_generation_matrix = np.zeros((agent_num, generation_num))
            column_name = strategy_params_list[param_id] + "_cov"
            for agent_id in range(0, agent_num):
                strategy_param_cov = df_filtered.loc[df_filtered["agent_id"] == agent_id][column_name].to_numpy()
                agent_generation_matrix[agent_id,:] = strategy_param_cov
            strategy_params_agent_generation_matrix_dict[strategy_params_list[param_id]] = agent_generation_matrix

        fig_scenario = "TS" + str(trainer_scenario_id) + "TPS" + str(trainer_params_scenario_id) + \
                       "P" + str(path_id)
        self.plotter.trainer_agent_strategy_params_cov_lines(strategy_params_agent_generation_matrix_dict,
                                                             fig_scenario,
                                                             strategy_params_legend_dict=strategy_params_legend_dict)

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
        fig_scenario = "TS" + str(trainer_scenario_id) + "TPS" + str(trainer_params_scenario_id) + \
                       "P" + str(path_id) + "G" + str(generation_id) + "_"
        self.plotter.trainer_agent_var_scatter(var_1_name, var_1_value,
                                               var_2_name, var_2_value,
                                               fig_scenario,
                                               area_value=area_value,
                                               var_1_lim=var_1_lim, var_2_lim=var_2_lim,
                                               var_1_label=var_1_label, var_2_label=var_2_label,
                                               fig_title=fig_title)

    def plot_trainer_env_var_evolution_path(self,
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
        fig_scenario = "_TS" + str(trainer_scenario_id) + "TPS" + str(trainer_params_scenario_id)
        self.plotter.trainer_env_var_evolution_path_line(var_name, var_value_dict, fig_scenario,
                                                         fig_title=fig_title, y_label=y_label, y_lim=y_lim)

    def plot_trainer_env_var_evolution_value_across_scenarios(self,
                                                              var_name: str,
                                                              df: pd.DataFrame,
                                                              trainer_scenario_id_list: list,
                                                              result_type: str = "convergence_level",
                                                              trainer_params_scenario_id: int = 0,
                                                              x_label=None,
                                                              y_label=None,
                                                              y_lim=None,
                                                              trainer_scenario_id_xticks=None,
                                                              unit_adjustment: float = 1):

        filter = {"trainer_scenario_id": 0,
                  "trainer_params_scenario_id": trainer_params_scenario_id}
        df_filtered = self.filter_dataframe(df, filter)
        path_id_set = set(df_filtered["path_id"])
        path_num = len(path_id_set)
        trainer_scenario_num = len(trainer_scenario_id_list)
        value_matrix = np.zeros((path_num, trainer_scenario_num))

        for path_counter, path_id in enumerate(path_id_set):
            for trainer_scenario_counter, trainer_scenario_id in enumerate(trainer_scenario_id_list):
                filter = {"trainer_scenario_id": trainer_scenario_id,
                          "trainer_params_scenario_id": trainer_params_scenario_id,
                          "path_id": path_id}
                df_filtered = self.filter_dataframe(df, filter)
                var_mean_name = var_name + "_mean"
                values = df_filtered[var_mean_name].to_numpy() * unit_adjustment
                if result_type == "average":
                    value_matrix[path_counter][trainer_scenario_counter] = values.mean()
                elif result_type == "convergence_level":
                    tail_length = int(len(values) * 0.1)
                    value_matrix[path_counter][trainer_scenario_counter] = values[-tail_length:-1].mean()
                else:
                    print("Result type is not implemented.")

        fig_scenario = "_TS" + str(trainer_scenario_id_list[0]) + "to" + str(trainer_scenario_id_list[-1]) + \
                       "TPS" + str(trainer_params_scenario_id)

        self.plotter.trainer_env_var_evolution_value_across_scenarios_line(
            var_name,
            value_matrix,
            fig_scenario,
            trainer_scenario_id_list,
            x_label=x_label,
            y_label=y_label,
            y_lim=y_lim,
            trainer_scenario_id_xticks=trainer_scenario_id_xticks
        )









