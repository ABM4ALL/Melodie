
import numpy as np
import pandas as pd
from typing import List

from Melodie import Analyzer
from .plotter import AspirationPlotter

class AspirationAnalyzer(Analyzer):
    plotter: AspirationPlotter

    def setup(self):
        self.trainer_scenarios = "trainer_scenarios"
        self.agent_trainer_result = "agent_trainer_result"
        self.agent_trainer_result_cov = "agent_trainer_result_cov"
        self.env_trainer_result = "env_trainer_result"
        self.env_trainer_result_cov = "env_trainer_result_cov"

    def plot_trainer_agent_strategy_params_convergence_heatmap(self, trainer_scenario_id, generation_id):
        strategy_params_list = ["strategy_param_1", "strategy_param_2", "strategy_param_3"]
        strategy_params_ticks = [r"$\alpha_{i, 1}$", r"$\alpha_{i, 2}$", r"$\alpha_{i, 3}$"]
        df = self.read_dataframe(self.agent_trainer_result_cov)
        self.plot_trainer_agent_strategy_params_cov_heatmap(strategy_params_list,
                                                            df,
                                                            trainer_scenario_id,
                                                            generation_id,
                                                            strategy_params_ticks=strategy_params_ticks)

    def plot_trainer_agent_strategy_params_convergence_lines(self,
                                                             trainer_scenario_id,
                                                             trainer_params_scenario_id: int = 0,
                                                             path_id: int = 0):
        strategy_params_list = ["strategy_param_1", "strategy_param_2", "strategy_param_3"]
        strategy_params_legend_dict = {
            "strategy_param_1": r"$\alpha_{i, 1}$",
            "strategy_param_2": r"$\alpha_{i, 2}$",
            "strategy_param_3": r"$\alpha_{i, 3}$"
        }
        df = self.read_dataframe(self.agent_trainer_result_cov)
        self.plot_trainer_agent_strategy_params_cov_lines(strategy_params_list,
                                                          df,
                                                          trainer_scenario_id,
                                                          strategy_params_legend_dict=strategy_params_legend_dict,
                                                          trainer_params_scenario_id=trainer_params_scenario_id,
                                                          path_id=path_id)

    def plot_trainer_env_strategy_shares(self, trainer_scenario_id):
        df = self.read_dataframe(self.env_trainer_result_cov)
        filter = {"trainer_scenario_id": trainer_scenario_id,
                  "trainer_params_scenario_id": 0,
                  "path_id": 0}
        df_filtered = self.filter_dataframe(df, filter)
        strategy_share_dict = {"exploration": df_filtered["exploration_accumulated_share_mean"].to_numpy(),
                               "exploitation": df_filtered["exploitation_accumulated_share_mean"].to_numpy(),
                               "imitation": df_filtered["imitation_accumulated_share_mean"].to_numpy()}
        fig_scenario = "TS" + str(trainer_scenario_id) + "TPS0P0"
        self.plotter.trainer_env_strategy_shares(
            strategy_share_dict,
            fig_scenario,
            y_lim=(0, 70)
        )

    def plot_trainer_env_average_net_performance(self, trainer_scenario_id):
        df = self.read_dataframe(self.env_trainer_result_cov)
        self.plot_trainer_env_var_evolution_path(
            "average_account", df,
            trainer_scenario_id=trainer_scenario_id,
            y_label="Average Final Net Performance",
            # y_lim=(800, 2600)，
            # y_lim=(-500, 2500)
            y_lim=(500, 4000)
        )

    def plot_trainer_env_average_technology(self, trainer_scenario_id):
        df = self.read_dataframe(self.env_trainer_result_cov)
        self.plot_trainer_env_var_evolution_path(
            "average_technology", df,
            trainer_scenario_id=trainer_scenario_id,
            y_label="Average Final Technology",
            # y_lim=(10, 40)，
            # y_lim=(5, 40)
            y_lim=(5, 60)
        )

    def plot_trainer_agent_s1s2_scatter(self, trainer_scenario_id):
        var_1_name = "exploration_count_mean"
        var_2_name = "exploitation_count_mean"
        generation_id = 49
        df = self.read_dataframe(self.agent_trainer_result_cov)
        self.plot_trainer_agent_var_scatter(var_1_name, var_2_name,
                                            df, trainer_scenario_id, generation_id,
                                            var_1_lim=(0, 25), var_2_lim=(0, 25),
                                            var_1_label="Exploration Count", var_2_label="Exploitation Count")

    def plot_trainer_env_var_strategy_cost_heatmap(self, env_var_name):
        df_scenario = self.read_dataframe(self.trainer_scenarios)
        df_result = self.read_dataframe(self.env_trainer_result_cov)
        # cost_exploration_list = [2, 4, 6, 8, 10]
        cost_exploration_list = [10, 8, 6, 4, 2]
        cost_imitation_list = [2, 4, 6, 8, 10]
        heat_matrix = np.zeros((len(cost_exploration_list), len(cost_imitation_list)))
        for cost_exploration_id, cost_exploration in enumerate(cost_exploration_list):
            for cost_imitation_id, cost_imitation in enumerate(cost_imitation_list):
                scenario_filter = {"aspiration_update_strategy": 1,
                                   "cost_exploration": cost_exploration,
                                   "cost_exploitation": 6,
                                   "cost_imitation": cost_imitation}
                df_scenario_filtered = self.filter_dataframe(df_scenario, scenario_filter)
                trainer_scenario_id = df_scenario_filtered.iloc[0]["id"]
                result_filter = {"trainer_scenario_id": trainer_scenario_id,
                                 "trainer_params_scenario_id": 0,
                                 "generation_id": 49,
                                 "path_id": 0}
                result_filtered = self.filter_dataframe(df_result, result_filter)
                heat_matrix[cost_exploration_id][cost_imitation_id] = round(result_filtered.iloc[0][env_var_name], 0)
        fig_scenario = env_var_name + "_TS_TPS0P0G49"
        # account
        # v_min = 900
        # v_max = 1700
        # technology
        v_min = 20
        v_max = 30
        self.plotter.trainer_env_var_strategy_cost_heatmap(
            heat_matrix,
            fig_scenario,
            imitation_cost_ticks=cost_imitation_list,
            exploration_cost_ticks=cost_exploration_list,
            v_min=v_min,
            v_max=v_max
        )

    def table_trainer_env_strategy_share_strategy_cost(self):
        df_scenario = self.read_dataframe(self.trainer_scenarios)
        df_result = self.read_dataframe(self.env_trainer_result_cov)
        # cost_exploration_list = [2, 4, 6, 8, 10]
        cost_exploration_list = [10, 8, 6, 4, 2]
        cost_imitation_list = [2, 4, 6, 8, 10]
        aspiration_update_strategy_list = [0, 1]
        result_columns = ["exploration_cost", "imitation_cost",
                          "historical_exploration_share", "historical_exploitation_share", "historical_imitation_share",
                          "social_exploration_share", "social_exploitation_share", "social_imitation_share"]
        result_table_name = "StrategyShare"
        result_table = []
        for cost_exploration_id, cost_exploration in enumerate(cost_exploration_list):
            for cost_imitation_id, cost_imitation in enumerate(cost_imitation_list):
                result_row = [cost_exploration, cost_imitation]
                for aspiration_update_strategy in aspiration_update_strategy_list:
                    scenario_filter = {"aspiration_update_strategy": aspiration_update_strategy,
                                       "cost_exploration": cost_exploration,
                                       "cost_exploitation": 6,
                                       "cost_imitation": cost_imitation}
                    df_scenario_filtered = self.filter_dataframe(df_scenario, scenario_filter)
                    trainer_scenario_id = df_scenario_filtered.iloc[0]["id"]
                    result_filter = {"trainer_scenario_id": trainer_scenario_id,
                                     "trainer_params_scenario_id": 0,
                                     "generation_id": 49,
                                     "path_id": 0}
                    result_filtered = self.filter_dataframe(df_result, result_filter)
                    exploration_share = result_filtered.iloc[0]["exploration_accumulated_share_mean"]
                    exploitation_share = result_filtered.iloc[0]["exploitation_accumulated_share_mean"]
                    imitation_share = result_filtered.iloc[0]["imitation_accumulated_share_mean"]
                    result_row += [exploration_share, exploitation_share, imitation_share]
                result_table.append(result_row)

        result_df_to_save = pd.DataFrame(result_table, columns=result_columns)
        self.conn.write_dataframe(result_table_name, result_df_to_save, if_exists='replace')

    def plot_trainer_env_var_evolution_result_across_scenarios(self,
                                                               env_var_name,
                                                               trainer_scenario_id_list: List[int],
                                                               result_type="convergence_level"):
        df = self.read_dataframe(self.env_trainer_result_cov)
        x_label = "Number of Firms"
        trainer_scenario_id_xticks = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500]

        # account
        y_label = "Average Final Net Performance"
        y_lim = (1000, 3000)
        # technology
        y_label = "Average Final Technology"
        y_lim = (20, 40)

        self.plot_trainer_env_var_evolution_value_across_scenarios(
            env_var_name,
            df,
            trainer_scenario_id_list,
            result_type=result_type,
            x_label=x_label,
            y_label=y_label,
            y_lim=y_lim,
            trainer_scenario_id_xticks=trainer_scenario_id_xticks
        )

    def plot_trainer_strategy_shares_across_scenarios(self,
                                                      trainer_scenario_id_list: List[int],
                                                      result_type="convergence_level",
                                                      trainer_params_scenario_id=0):

        df = self.read_dataframe(self.env_trainer_result_cov)
        x_label = "Number of Firms"
        trainer_scenario_id_xticks = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500]
        y_lim = (0, 40)

        filter = {"trainer_scenario_id": 0,
                  "trainer_params_scenario_id": 0}
        df_filtered = self.filter_dataframe(df, filter)
        path_id_set = set(df_filtered["path_id"])
        path_num = len(path_id_set)
        trainer_scenario_num = len(trainer_scenario_id_list)

        strategy_name_list = ["exploration", "exploitation", "imitation"]
        strategy_matrix_dict = {}
        for strategy_name in strategy_name_list:
            value_matrix = np.zeros((path_num, trainer_scenario_num))
            for path_counter, path_id in enumerate(path_id_set):
                for trainer_scenario_counter, trainer_scenario_id in enumerate(trainer_scenario_id_list):
                    filter = {"trainer_scenario_id": trainer_scenario_id,
                              "trainer_params_scenario_id": trainer_params_scenario_id,
                              "path_id": path_id}
                    df_filtered = self.filter_dataframe(df, filter)
                    var_mean_name = strategy_name + "_accumulated_share_mean"
                    values = df_filtered[var_mean_name].to_numpy() * 100
                    if result_type == "average":
                        value_matrix[path_counter][trainer_scenario_counter] = values.mean()
                    elif result_type == "convergence_level":
                        tail_length = int(len(values) * 0.1)
                        value_matrix[path_counter][trainer_scenario_counter] = values[-tail_length:-1].mean()
                    else:
                        print("Result type is not implemented.")
            strategy_matrix_dict[strategy_name] = value_matrix

        fig_name = "trainer_env_evolution_technology_share_TS" + str(trainer_scenario_id_list[0]) + "to" + \
                   str(trainer_scenario_id_list[-1]) + "TPS" + str(trainer_params_scenario_id)

        self.plotter.trainer_env_var_evolution_strategy_shares_across_scenarios_line(
            strategy_name_list,
            strategy_matrix_dict,
            trainer_scenario_id_list,
            fig_name,
            x_label=x_label,
            y_lim=y_lim,
            trainer_scenario_id_xticks=trainer_scenario_id_xticks
        )




    def run(self):

        """
        Plot for individual scenarios - based and extreme cases
        """
        # scenario_list = [0, 125] # two base scenarios
        scenario_list = [250, 251, 252, 253, 254, 255] # extreme cases
        for scenario_id in scenario_list:

            # --- convergence
            # self.plot_trainer_agent_strategy_params_convergence_heatmap(scenario_id, 0)
            # self.plot_trainer_agent_strategy_params_convergence_heatmap(scenario_id, 49)

            # --- evolution
            # self.plot_trainer_env_strategy_shares(scenario_id)
            # self.plot_trainer_env_average_net_performance(scenario_id)
            # self.plot_trainer_env_average_technology(scenario_id)

            # --- other
            # self.plot_trainer_agent_strategy_params_convergence_lines(scenario_id)
            # self.plot_trainer_agent_s1s2_scatter(scenario_id)

            pass

        """
        Plot for scenarios of technology search costs combinations
        """
        # self.plot_trainer_env_var_strategy_cost_heatmap("average_account_mean")
        # self.plot_trainer_env_var_strategy_cost_heatmap("average_technology_mean")
        # self.table_trainer_env_strategy_share_strategy_cost()

        """
        Plot for scenarios of different firm numbers
        """
        scenarios_group = [list(range(256, 266)), list(range(266, 276))]
        for scenario_list in scenarios_group:
            self.plot_trainer_strategy_shares_across_scenarios(scenario_list)
            # self.plot_trainer_env_var_evolution_result_across_scenarios("average_account", scenario_list)
            # self.plot_trainer_env_var_evolution_result_across_scenarios("average_technology", scenario_list)
            pass










