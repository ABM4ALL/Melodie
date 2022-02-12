
import numpy as np
import pandas as pd

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

    def plot_trainer_agent_strategy_params_convergence(self, trainer_scenario_id, generation_id):
        strategy_params_list = ["strategy_param_1", "strategy_param_2", "strategy_param_3"]
        strategy_params_ticks = [r"$\alpha_{i, 1}$", r"$\alpha_{i, 2}$", r"$\alpha_{i, 3}$"]
        df = self.read_dataframe(self.agent_trainer_result_cov)
        self.plot_trainer_agent_strategy_params_cov_heatmap(strategy_params_list,
                                                            df,
                                                            trainer_scenario_id,
                                                            generation_id,
                                                            strategy_params_ticks=strategy_params_ticks)

    def plot_trainer_env_average_technology(self, trainer_scenario_id):
        df = self.read_dataframe(self.env_trainer_result_cov)
        self.plot_trainer_env_var(
            "average_technology", df,
            trainer_scenario_id=trainer_scenario_id,
            y_label="Average Technology",
            # y_lim=(0, 50) # historical,
            y_lim=(0, 10)  # social
        )

    def plot_trainer_agent_s1s2_scatter(self, trainer_scenario_id):
        var_1_name = "strategy_param_1_mean"
        var_2_name = "strategy_param_2_mean"
        generation_id = 49
        df = self.read_dataframe(self.agent_trainer_result_cov)
        self.plot_trainer_agent_var_scatter(var_1_name, var_2_name,
                                            df, trainer_scenario_id, generation_id,
                                            var_1_lim=(0, 100), var_2_lim=(0, 100),
                                            var_1_label="Strategy Parameter 1", var_2_label="Strategy Parameter 2")

    def plot_trainer_env_strategy_shares(self, trainer_scenario_id):
        df = self.read_dataframe(self.env_trainer_result_cov)
        filter = {"trainer_scenario_id": trainer_scenario_id,
                  "trainer_params_scenario_id": 0,
                  "path_id": 0}
        df_filtered = self.filter_dataframe(df, filter)
        strategy_share_dict = {"exploration": df_filtered["exploration_accumulated_share_mean"].to_numpy(),
                               "exploitation": df_filtered["exploitation_accumulated_share_mean"].to_numpy(),
                               "imitation": df_filtered["imitation_accumulated_share_mean"].to_numpy()}
        fig_scenario = "_TS" + str(trainer_scenario_id) + "TPS0P0_"
        self.plotter.trainer_env_strategy_shares(strategy_share_dict, fig_scenario)

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
                heat_matrix[cost_exploration_id][cost_imitation_id] = result_filtered.iloc[0][env_var_name]
        fig_scenario = env_var_name + "_TS_TPS0P0G49"
        self.plotter.trainer_env_var_strategy_cost_heatmap(heat_matrix,
                                                           fig_scenario,
                                                           imitation_cost_ticks=cost_imitation_list,
                                                           exploration_cost_ticks=cost_exploration_list)

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

    def run(self):
        # self.plot_trainer_agent_strategy_params_convergence(0, 0)
        # self.plot_trainer_agent_strategy_params_convergence(0, 49)
        # self.plot_trainer_agent_s1s2_scatter(0)
        # self.plot_trainer_env_average_technology(0)
        # self.plot_trainer_env_strategy_shares(0)
        # self.plot_trainer_env_var_strategy_cost_heatmap("average_technology_mean")
        self.plot_trainer_env_var_strategy_cost_heatmap("average_account_mean")
        # self.table_trainer_env_strategy_share_strategy_cost()



        # exploration, exploitation, imitation costs
        special_scenarios = [
            0,  # 2, 2, 2, historical
            # 4, # 10, 2, 2, historical
            # 20, # 2, 10, 2, historical
            # 100,  # 2, 2, 10, historical
            # 124,  # 10, 10, 10, historical
            # 125,  # 2, 2, 2, social
            # 129,  # 10, 2, 2, social
            # 145, # 2, 10, 2, social
            # 225,  # 2, 2, 10, social
            # 249,  # 10, 10, 10, social
        ]

        # for scenario_id in special_scenarios:
        #     self.plot_trainer_env_average_technology(scenario_id)
        #     self.plot_trainer_env_strategy_shares(scenario_id)








