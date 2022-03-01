
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict

from Melodie import Plotter

class AspirationPlotter(Plotter):

    def trainer_env_strategy_shares(self, strategy_share_dict, fig_scenario, y_lim=None):

        figure = plt.figure(figsize=(12, 6), dpi=self.fig_dpi, frameon=False)
        ax = figure.add_axes((0.1, 0.15, 0.8, 0.75))
        generation_array = np.array((range(len(strategy_share_dict["exploration"])))) + 0.5

        exploration_values = strategy_share_dict["exploration"] * 100
        exploitation_values = strategy_share_dict["exploitation"] * 100
        imitation_values = strategy_share_dict["imitation"] * 100
        ax.bar(generation_array, exploration_values, width=1, label='exploration')
        ax.bar(generation_array, exploitation_values, width=1, bottom=exploration_values, label='exploitation')
        ax.bar(generation_array, imitation_values, width=1, bottom=exploration_values + exploitation_values, label='imitation')

        figure.legend(fontsize=15, bbox_to_anchor=(0, 1.02, 1, 0.1), bbox_transform=ax.transAxes,
                      loc='lower left', ncol=3, borderaxespad=0, mode='expand', frameon=True)
        if y_lim != None: ax.set_ylim(y_lim)
        ax.set_xlabel("Generation", fontsize=15, labelpad=10)
        ax.set_ylabel("Technology Search Strategy Share (%)", fontsize=15, labelpad=10)
        ax.grid(True)

        ax.get_yaxis().get_major_formatter().set_useOffset(False)
        for tick in ax.xaxis.get_major_ticks():
            tick.label1.set_fontsize(15)
        for tick in ax.yaxis.get_major_ticks():
            tick.label1.set_fontsize(15)

        fig_name = "trainer_strategy_shares_" + fig_scenario
        self.save_fig(figure, fig_name)

    def trainer_env_var_heatmap(self,
                                env_var_matrix: np.ndarray,
                                fig_name: str,
                                param1_values_ticks: list,
                                param2_values_ticks: list,
                                param1_label: str,
                                param2_label: str,
                                v_min: float = None,
                                v_max: float = None):

        figure = plt.figure(figsize=(6, 4.5),
                            dpi=self.fig_dpi, frameon=False)
        ax = figure.add_axes((0.15, 0.15, 0.8, 0.8))

        if v_min == None and v_max == None:
            ax = sns.heatmap(env_var_matrix, annot=True, fmt="g", linewidths=.5,
                             xticklabels=param2_values_ticks, yticklabels=param1_values_ticks)
        else:
            ax = sns.heatmap(env_var_matrix, annot=True, fmt="g", linewidths=.5,
                             xticklabels=param2_values_ticks, yticklabels=param1_values_ticks,
                             vmin=v_min, vmax=v_max)

        ax.set_xlabel(param2_label,
                      fontsize=15,
                      labelpad=10)
        ax.set_ylabel(param1_label,
                      fontsize=15,
                      labelpad=10)

        plt.xticks(rotation=0.00001)
        plt.yticks(rotation=0.00001)

        for tick in ax.xaxis.get_major_ticks():
            tick.label1.set_fontsize(15)
        for tick in ax.yaxis.get_major_ticks():
            tick.label1.set_fontsize(15)

        self.save_fig(figure, fig_name)

    def trainer_env_var_evolution_strategy_shares_across_scenarios_line(self,
                                                                        strategy_name_list: List[str],
                                                                        strategy_matrix_dict: Dict[str, np.ndarray],
                                                                        trainer_scenario_id_list: List[int],
                                                                        fig_name,
                                                                        x_label=None,
                                                                        y_lim=None,
                                                                        trainer_scenario_id_xticks: list = None):

        figure = plt.figure(
            figsize=self.trainer_env_var_evolution_value_across_scenarios_fig_size,
            dpi=self.fig_dpi,
            frameon=False
        )
        ax = figure.add_axes(self.trainer_env_var_evolution_value_across_scenarios_fig_axe_area)
        color_counter = 0
        for strategy_name in strategy_name_list:
            value_matrix = strategy_matrix_dict[strategy_name]
            value_mean = value_matrix.mean(axis=0)
            value_std = value_matrix.std(axis=0)
            generation_list = [i + 1 for i in range(len(value_mean))]
            ax.plot(generation_list, value_mean,
                    linewidth=self.trainer_env_var_evolution_value_across_scenarios_mean_linewidth,
                    linestyle=self.trainer_env_var_evolution_value_across_scenarios_mean_linestyle,
                    # color=self.colors[color_counter],
                    label=strategy_name)
            ax.fill_between(generation_list,
                            value_mean + value_std,
                            value_mean - value_std,
                            alpha=self.trainer_env_var_evolution_value_across_scenarios_std_alpha,
                            # facecolor=self.colors[color_counter],
                            )
            color_counter += 1

        figure.legend(fontsize=15, bbox_to_anchor=(0, 1.02, 1, 0.1), bbox_transform=ax.transAxes,
                      loc='lower left', ncol=3, borderaxespad=0, mode='expand', frameon=True)
        ax.set_ylabel("Technology Search Strategy Share (%)",
                      fontsize=self.trainer_env_var_evolution_value_across_scenarios_x_label_fontsize,
                      labelpad=self.trainer_env_var_evolution_value_across_scenarios_x_labelpad)
        ax.set_xlabel(self.check_if_no_label_use_var_name(x_label,
                                                          self.trainer_env_var_evolution_value_across_scenarios_x_label),
                      fontsize=self.trainer_env_var_evolution_value_across_scenarios_y_label_fontsize,
                      labelpad=self.trainer_env_var_evolution_value_across_scenarios_y_labelpad)

        if y_lim != None: ax.set_ylim(y_lim)
        ax.grid(self.trainer_env_var_evolution_value_across_scenarios_grid)

        x_ticks_labels = self.check_if_no_label_use_var_name(trainer_scenario_id_xticks, trainer_scenario_id_list)
        ax.set_xticks(generation_list, labels=x_ticks_labels)

        ax.get_yaxis().get_major_formatter().set_useOffset(False)
        for tick in ax.xaxis.get_major_ticks():
            tick.label1.set_fontsize(self.trainer_env_var_evolution_value_across_scenarios_x_tick_fontsize)
        for tick in ax.yaxis.get_major_ticks():
            tick.label1.set_fontsize(self.trainer_env_var_evolution_value_across_scenarios_y_tick_fontsize)

        self.save_fig(figure, fig_name)











