import numpy as np
import pandas as pd
from abc import ABC
from typing import ClassVar, Dict

from .config import Config
from .db import create_db_conn, DBConn
from .plotter import Plotter


class Analyzer(ABC):
    def __init__(self, config: Config, plotter_cls: ClassVar[Plotter] = Plotter):
        self.config = config
        self.plotter = plotter_cls(config)
        self.setup()
        self.conn = self.create_db_conn(config)

    def setup(self):
        pass

    def create_db_conn(self, config) -> "DBConn":
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

    def plot_trainer_agent_strategy_params_convergence_heatmap(
        self,
        agent_trainer_result_cov: pd.DataFrame,
        strategy_params: list,
        trainer_scenario_id: int,
        generation_id: int,
        trainer_params_scenario_id: int = 0,
        path_id: int = 0,
        ylim: tuple = None,
        strategy_params_labels: list = None,
        fig_suffix: str = None,
    ):

        filter = {
            "trainer_scenario_id": trainer_scenario_id,
            "trainer_params_scenario_id": trainer_params_scenario_id,
            "path_id": path_id,
            "generation_id": generation_id,
        }
        df_filtered = self.filter_dataframe(agent_trainer_result_cov, filter)
        df_filtered = df_filtered.fillna(0)
        agent_num = len(df_filtered)
        params_num = len(strategy_params)
        cov_matrix = np.zeros((params_num, agent_num))
        for param_id in range(0, len(strategy_params)):
            column_name = strategy_params[param_id] + "_cov"
            param_cov = df_filtered[column_name].to_numpy()
            cov_matrix[param_id, :] = param_cov
        self.plotter.trainer_agent_strategy_params_convergence_heatmap(
            cov_matrix,
            ylim=ylim,
            fig_suffix=fig_suffix,
            strategy_params_labels=strategy_params_labels,
        )

    def plot_trainer_agent_strategy_params_convergence_lines(
        self,
        agent_trainer_result_cov: pd.DataFrame,
        strategy_params_list: list,
        trainer_scenario_id: int,
        trainer_params_scenario_id: int = 0,
        path_id: int = 0,
        ylim: tuple = None,
        strategy_params_labels: list = None,
        fig_suffix: str = None,
    ):
        filter = {
            "trainer_scenario_id": trainer_scenario_id,
            "trainer_params_scenario_id": trainer_params_scenario_id,
            "path_id": path_id,
        }
        df_filtered = self.filter_dataframe(agent_trainer_result_cov, filter)
        df_filtered = df_filtered.fillna(0)
        generation_num = len(df_filtered.loc[df_filtered["agent_id"] == 0])
        agent_num = len(df_filtered.loc[df_filtered["generation_id"] == 0])
        strategy_params_agent_generation_matrix_dict: Dict[str, np.ndarray] = {}
        for param_id in range(0, len(strategy_params_list)):
            agent_generation_matrix = np.zeros((agent_num, generation_num))
            column_name = strategy_params_list[param_id] + "_cov"
            for agent_id in range(0, agent_num):
                strategy_param_cov = df_filtered.loc[
                    df_filtered["agent_id"] == agent_id
                ][column_name].to_numpy()
                agent_generation_matrix[agent_id, :] = strategy_param_cov
            strategy_params_agent_generation_matrix_dict[
                strategy_params_list[param_id]
            ] = agent_generation_matrix

        self.plotter.trainer_agent_strategy_params_convergence_lines(
            strategy_params_agent_generation_matrix_dict,
            ylim=ylim,
            fig_suffix=fig_suffix,
            strategy_params_labels=strategy_params_labels,
        )

    def plot_trainer_env_var_evolution_lines(
        self,
        var_name: str,
        env_trainer_result_cov: pd.DataFrame,
        trainer_scenario_id: int,
        trainer_params_scenario_id: int = 0,
        path_id: int = None,
        y_label: str = None,
        y_lim: tuple = None,
        legend_ncol: int = None,
        fig_suffix: str = None,
    ):

        filter = {
            "trainer_scenario_id": trainer_scenario_id,
            "trainer_params_scenario_id": trainer_params_scenario_id,
        }
        if path_id != None:
            filter["path_id"] = path_id
        df_filtered = self.filter_dataframe(env_trainer_result_cov, filter)

        var_mean_name = var_name + "_mean"
        var_cov_name = var_name + "_cov"
        var_value_dict = {}
        path_id_set = set(df_filtered["path_id"])
        for path_id in path_id_set:
            key = "path_" + str(path_id)
            df_filtered_path_id = df_filtered.loc[df_filtered["path_id"] == path_id]
            var_value_dict[key] = [
                df_filtered_path_id[var_mean_name].to_numpy(),
                df_filtered_path_id[var_cov_name].to_numpy(),
            ]

        self.plotter.trainer_env_var_evolution_lines(
            var_name,
            var_value_dict,
            y_label=y_label,
            y_lim=y_lim,
            legend_ncol=legend_ncol,
            fig_suffix=fig_suffix,
        )

    def plot_trainer_agent_vars_scatter(
        self,
        var_1_name: str,
        var_2_name: str,
        agent_trainer_result_cov: pd.DataFrame,
        trainer_scenario_id: int,
        generation_id: int,
        trainer_params_scenario_id: int = 0,
        path_id: int = 0,
        fig_suffix: str = None,
        area_value: np.array = None,
        var_1_lim=None,
        var_2_lim=None,
        var_1_label=None,
        var_2_label=None,
    ):
        filter = {
            "trainer_scenario_id": trainer_scenario_id,
            "trainer_params_scenario_id": trainer_params_scenario_id,
            "path_id": path_id,
            "generation_id": generation_id,
        }
        df_filtered = self.filter_dataframe(agent_trainer_result_cov, filter)
        var_1_value = df_filtered[var_1_name].to_numpy()
        var_2_value = df_filtered[var_2_name].to_numpy()
        self.plotter.trainer_agent_vars_scatter(
            var_1_name,
            var_1_value,
            var_2_name,
            var_2_value,
            area_value=area_value,
            var_1_lim=var_1_lim,
            var_2_lim=var_2_lim,
            var_1_label=var_1_label,
            var_2_label=var_2_label,
            fig_suffix=fig_suffix,
        )

    def plot_trainer_env_var_across_scenarios(
        self,
        scenario_var_info: dict,
        env_var_info: dict,
        env_trainer_result_cov: pd.DataFrame,
        result_type: str = "convergence_level",
        trainer_params_scenario_id: int = 0,
        fig_suffix: str = None,
        unit_adjustment: float = 1,
    ):

        filter = {
            "trainer_scenario_id": 0,
            "trainer_params_scenario_id": trainer_params_scenario_id,
        }
        df_filtered = self.filter_dataframe(env_trainer_result_cov, filter)
        path_id_set = set(df_filtered["path_id"])
        number_of_path = len(path_id_set)
        number_of_scenario = len(scenario_var_info["scenario_id_list"])
        value_matrix = np.zeros((number_of_path, number_of_scenario))

        for path_counter, path_id in enumerate(path_id_set):
            for trainer_scenario_counter, trainer_scenario_id in enumerate(
                scenario_var_info["scenario_id_list"]
            ):
                filter = {
                    "trainer_scenario_id": trainer_scenario_id,
                    "trainer_params_scenario_id": trainer_params_scenario_id,
                    "path_id": path_id,
                }
                df_filtered = self.filter_dataframe(env_trainer_result_cov, filter)
                env_var_mean_name = env_var_info["var"] + "_mean"
                values = df_filtered[env_var_mean_name].to_numpy() * unit_adjustment
                if result_type == "average":
                    value_matrix[path_counter][trainer_scenario_counter] = values.mean()
                elif result_type == "convergence_level":
                    tail_length = int(len(values) * 0.1)
                    value_matrix[path_counter][trainer_scenario_counter] = values[
                        -tail_length:-1
                    ].mean()
                else:
                    print("Result type is not implemented.")

        self.plotter.trainer_env_var_across_scenarios_line(
            value_matrix,
            x_label=scenario_var_info["x_label"],
            y_label=env_var_info["y_label"],
            y_lim=env_var_info["y_lim"],
            x_ticks=scenario_var_info["x_ticks"],
            fig_suffix=fig_suffix,
        )
