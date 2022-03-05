
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, List
import seaborn as sns
import matplotlib.pyplot as plt

from .config import Config

class Plotter(ABC):

    def __init__(self, config: Config):
        self.fig_folder = config.output_folder
        self.setup_common_fig_params()
        self.setup_agent_strategy_convergence_heatmap_fig_params()
        self.setup_agent_strategy_convergence_lines_fig_params()
        self.setup_trainer_agent_vars_scatter_fig_params()
        self.setup_env_var_evolution_lines_fig_params()
        self.setup_trainer_env_var_across_scenarios_fig_params()
        self.setup_colors()
        self.setup()

    def setup_common_fig_params(self):
        self.fig_format = "PNG"
        self.fig_dpi = 200
        self.line_width = 1.5
        self.line_style = '-'
        self.alpha = 0.2
        self.x_label_fontsize = 15
        self.x_labelpad = 6
        self.y_label_fontsize = 15
        self.y_labelpad = 6
        self.x_tick_fontsize = 15
        self.y_tick_fontsize = 15
        self.scatter_area = 10
        self.grid = True

    def setup_agent_strategy_convergence_heatmap_fig_params(self):
        self.agent_strategy_convergence_heatmap_prefix = "agent_strategy_convergence_heatmap"
        self.agent_strategy_convergence_heatmap_fig_size = (20, 3)
        self.agent_strategy_convergence_heatmap_fig_axe_area = (0.05, 0.2, 0.94, 0.7)
        self.agent_strategy_convergence_heatmap_vlim = (0, 1)
        self.agent_strategy_convergence_heatmap_x_label = "Agent"
        self.agent_strategy_convergence_heatmap_y_label = "Strategy Parameter"

    def setup_agent_strategy_convergence_lines_fig_params(self):
        self.agent_strategy_convergence_lines_prefix = "agent_strategy_convergence_lines"
        self.agent_strategy_convergence_lines_fig_size = (12, 6)
        self.agent_strategy_convergence_lines_fig_axe_area = (0.1, 0.15, 0.8, 0.75)
        self.agent_strategy_convergence_lines_std_boolean = True
        self.agent_strategy_convergence_lines_ylim = (0, 1)
        self.agent_strategy_convergence_lines_x_label = "Generation"
        self.agent_strategy_convergence_lines_y_label = "Coefficient of Variance"

    def setup_env_var_evolution_lines_fig_params(self):
        self.env_var_evolution_lines_prefix = "env_var_evolution_lines"
        self.env_var_evolution_fig_size = (12, 6)
        self.env_var_evolution_fig_axe_area = (0.1, 0.15, 0.8, 0.75)
        self.env_var_evolution_x_label = "Generation"

    def setup_trainer_agent_vars_scatter_fig_params(self):
        self.agent_vars_scatter_prefix = "agent_vars_scatter"
        self.agent_vars_scatter_size = (6, 6)
        self.agent_vars_scatter_axe_area = (0.15, 0.15, 0.8, 0.8)

    def setup_trainer_env_var_across_scenarios_fig_params(self):
        self.trainer_env_var_across_scenarios_prefix = "trainer_env_var_across_scenarios"
        self.trainer_env_var_across_scenarios_fig_size = (12, 6)
        self.trainer_env_var_across_scenarios_fig_axe_area = (0.1, 0.15, 0.8, 0.75)

    def setup_colors(self):
        self.colors = ["tab:orange", "tab:blue", "tab:green", "tab:red", "tab:purple",
                       "tab:brown", "tab:pink", "tab:gray", "tab:olive", "tab:cyan",
                       "dimgray", "lightcoral", "tomato", "peru", "darkorange", "gold",
                       "olivedrab", "lime", "darkslategrey", "royalblue", "violet",
                       "navy", "crimson"]

    def setup(self):
        pass

    def check_if_input_none_use_default(self, input, default):
        if input == None:
            value = default
        else:
            value = input
        return value

    def add_suffix_if_exist(self, prefix, suffix):
        fig_name = prefix
        if suffix == None:
            pass
        else:
            fig_name += suffix
        return fig_name

    def calc_legend_ncol(self, legend_num: int) -> int:
        ncol = 2
        if legend_num in [2, 4]:
            pass
        elif legend_num in [3, 5, 6, 9]:
            ncol = 3
        elif legend_num in [7, 8] or legend_num >= 10:
            ncol = 4
        return ncol

    def save_fig(self, fig, fig_name):
        fig.savefig(self.fig_folder + "/" + fig_name + ".png", dpi=self.fig_dpi, format=self.fig_format)
        plt.close(fig)

    def trainer_agent_strategy_params_convergence_heatmap(self,
                                                          strategy_params_cov_matrix: np.ndarray,
                                                          ylim: tuple = None,
                                                          fig_suffix: str = None,
                                                          strategy_params_labels: list = None):

        figure = plt.figure(figsize=self.agent_strategy_convergence_heatmap_fig_size,
                            dpi=self.fig_dpi, frameon=False)
        ax = figure.add_axes(self.agent_strategy_convergence_heatmap_fig_axe_area)

        x_ticks = [i + 1 for i in range(0, strategy_params_cov_matrix.shape[1])]
        y_ticks = [i + 1 for i in range(0, strategy_params_cov_matrix.shape[0])]
        if strategy_params_labels != None: y_ticks = strategy_params_labels

        ylim = self.check_if_input_none_use_default(ylim, self.agent_strategy_convergence_heatmap_vlim)
        ax = sns.heatmap(
            strategy_params_cov_matrix,
            vmin=ylim[0],
            vmax=ylim[1],
            xticklabels=x_ticks,
            yticklabels=y_ticks
        )

        ax.set_xlabel(self.agent_strategy_convergence_heatmap_x_label,
                      fontsize=self.x_label_fontsize,
                      labelpad=self.x_labelpad)
        ax.set_ylabel(self.agent_strategy_convergence_heatmap_y_label,
                      fontsize=self.y_label_fontsize,
                      labelpad=self.y_labelpad)

        plt.xticks(rotation=0.00001)
        plt.yticks(rotation=0.00001)

        for tick in ax.xaxis.get_major_ticks():
            tick.label1.set_fontsize(self.x_tick_fontsize)
        for tick in ax.yaxis.get_major_ticks():
            tick.label1.set_fontsize(self.y_tick_fontsize)

        fig_name = self.add_suffix_if_exist(self.agent_strategy_convergence_heatmap_prefix, fig_suffix)
        self.save_fig(figure, fig_name)

    def trainer_agent_strategy_params_convergence_lines(self,
                                                        strategy_params_agent_generation_matrix_dict: Dict[str, np.ndarray],
                                                        ylim: tuple = None,
                                                        fig_suffix: str = None,
                                                        strategy_params_labels: dict = None,
                                                        legend_ncol: int = None):

        figure = plt.figure(figsize=self.agent_strategy_convergence_lines_fig_size,
                            dpi=self.fig_dpi, frameon=False)
        ax = figure.add_axes(self.agent_strategy_convergence_lines_fig_axe_area)

        param_counter = 0
        for strategy_param, agent_generation_matrix in strategy_params_agent_generation_matrix_dict.items():

            strategy_param_cov_mean = agent_generation_matrix.mean(axis=0)
            strategy_param_cov_std = agent_generation_matrix.std(axis=0)
            generation_list = list(range(len(strategy_param_cov_mean)))

            ax.plot(generation_list, strategy_param_cov_mean,
                    linewidth=self.line_width,
                    linestyle=self.line_style,
                    color=self.colors[param_counter],
                    label=strategy_params_labels[param_counter])
            if self.agent_strategy_convergence_lines_std_boolean:
                ax.fill_between(generation_list,
                                strategy_param_cov_mean - strategy_param_cov_std,
                                strategy_param_cov_mean + strategy_param_cov_std,
                                alpha=self.alpha,
                                facecolor=self.colors[param_counter])
            param_counter += 1

        ylim = self.check_if_input_none_use_default(ylim, self.agent_strategy_convergence_lines_ylim)
        ax.set_ylim(ylim)
        ax.grid(self.grid)

        if len(strategy_params_labels) > 1:
            ncol = self.check_if_input_none_use_default(legend_ncol, self.calc_legend_ncol(len(strategy_params_labels)))
            figure.legend(fontsize=15, bbox_to_anchor=(0, 1.02, 1, 0.1), bbox_transform=ax.transAxes,
                          loc='lower left', ncol=ncol, borderaxespad=0, mode='expand', frameon=True)

        ax.set_xlabel(self.agent_strategy_convergence_lines_x_label,
                      fontsize=self.x_label_fontsize,
                      labelpad=self.x_labelpad)
        ax.set_ylabel(self.agent_strategy_convergence_lines_y_label,
                      fontsize=self.y_label_fontsize,
                      labelpad=self.y_labelpad)

        for tick in ax.xaxis.get_major_ticks():
            tick.label1.set_fontsize(self.x_tick_fontsize)
        for tick in ax.yaxis.get_major_ticks():
            tick.label1.set_fontsize(self.y_tick_fontsize)

        fig_name = self.add_suffix_if_exist(self.agent_strategy_convergence_lines_prefix, fig_suffix)
        self.save_fig(figure, fig_name)

    def trainer_env_var_evolution_lines(self,
                                        var_name: str,
                                        var_value_dict: dict,
                                        y_label: str = None,
                                        y_lim: tuple = None,
                                        legend_ncol: int = None,
                                        fig_suffix: str = None):

        figure = plt.figure(figsize=self.env_var_evolution_fig_size, dpi=self.fig_dpi, frameon=False)
        ax = figure.add_axes(self.env_var_evolution_fig_axe_area)

        color_counter = 0
        for key, value in var_value_dict.items():
            path_name = key
            path_var_mean = value[0]
            path_var_cov = value[1]
            generation_list = list(range(len(path_var_mean)))
            ax.plot(generation_list, path_var_mean,
                    linewidth=self.line_width,
                    linestyle=self.line_style,
                    color=self.colors[color_counter],
                    label=path_name)
            ax.fill_between(generation_list,
                            path_var_mean * (1 - path_var_cov),
                            path_var_mean * (1 + path_var_cov),
                            alpha=self.alpha,
                            facecolor=self.colors[color_counter])
            color_counter += 1
            if color_counter == len(self.colors):
                color_counter = np.random.randint(0, len(self.colors))

        ax.set_ylabel(self.check_if_input_none_use_default(y_label, var_name),
                      fontsize=self.x_label_fontsize,
                      labelpad=self.x_labelpad)
        ax.set_xlabel(self.env_var_evolution_x_label,
                      fontsize=self.y_label_fontsize,
                      labelpad=self.y_labelpad)

        if y_lim != None: ax.set_ylim(y_lim)
        ax.grid(self.grid)

        if len(var_value_dict) > 1:
            ncol = self.check_if_input_none_use_default(legend_ncol, self.calc_legend_ncol(len(var_value_dict)))
            figure.legend(fontsize=15, bbox_to_anchor=(0, 1.02, 1, 0.1), bbox_transform=ax.transAxes,
                          loc='lower left', ncol=ncol, borderaxespad=0, mode='expand', frameon=True)

        ax.get_yaxis().get_major_formatter().set_useOffset(False)
        for tick in ax.xaxis.get_major_ticks():
            tick.label1.set_fontsize(self.x_tick_fontsize)
        for tick in ax.yaxis.get_major_ticks():
            tick.label1.set_fontsize(self.y_tick_fontsize)

        fig_name = self.add_suffix_if_exist(self.env_var_evolution_lines_prefix, fig_suffix)
        self.save_fig(figure, fig_name)

    def trainer_agent_vars_scatter(self,
                                   var_1_name, var_1_value,
                                   var_2_name, var_2_value,
                                   area_value=None,
                                   var_1_lim=None, var_2_lim=None,
                                   var_1_label=None, var_2_label=None,
                                   fig_suffix: str = None):

        figure = plt.figure(figsize=self.agent_vars_scatter_size, dpi=self.fig_dpi, frameon=False)
        ax = figure.add_axes(self.agent_vars_scatter_axe_area)

        if area_value == None:
            area = self.scatter_area
        else:
            area = area_value
        ax.scatter(var_1_value, var_2_value, s=area, c=self.colors[0], alpha=0.5)

        ax.set_xlabel(self.check_if_input_none_use_default(var_1_label, var_1_name),
                      fontsize=self.x_label_fontsize,
                      labelpad=self.x_labelpad)
        ax.set_ylabel(self.check_if_input_none_use_default(var_2_label, var_2_name),
                      fontsize=self.y_label_fontsize,
                      labelpad=self.y_labelpad)

        if var_1_lim != None: ax.set_xlim(var_1_lim)
        if var_2_lim != None: ax.set_ylim(var_2_lim)
        ax.grid(self.grid)

        ax.get_yaxis().get_major_formatter().set_useOffset(False)
        for tick in ax.xaxis.get_major_ticks():
            tick.label1.set_fontsize(self.x_tick_fontsize)
        for tick in ax.yaxis.get_major_ticks():
            tick.label1.set_fontsize(self.y_tick_fontsize)

        fig_name = self.add_suffix_if_exist(self.agent_vars_scatter_prefix, fig_suffix)
        self.save_fig(figure, fig_name)

    def trainer_env_var_across_scenarios_line(self,
                                              value_matrix: np.ndarray,
                                              x_label: str,
                                              y_label: str,
                                              y_lim: str,
                                              x_ticks: list,
                                              fig_suffix: str = None):

        figure = plt.figure(
            figsize=self.trainer_env_var_across_scenarios_fig_size,
            dpi=self.fig_dpi,
            frameon=False
        )
        ax = figure.add_axes(self.trainer_env_var_across_scenarios_fig_axe_area)
        value_mean = value_matrix.mean(axis=0)
        value_std = value_matrix.std(axis=0)
        generation_list = [i + 1 for i in range(len(value_mean))]
        ax.plot(generation_list, value_mean,
                linewidth=self.line_width,
                linestyle=self.line_style,
                color=self.colors[0])
        ax.fill_between(generation_list,
                        value_mean + value_std,
                        value_mean - value_std,
                        alpha=self.alpha,
                        facecolor=self.colors[0])

        ax.set_ylabel(y_label,
                      fontsize=self.x_label_fontsize,
                      labelpad=self.x_labelpad)
        ax.set_xlabel(x_label,
                      fontsize=self.y_label_fontsize,
                      labelpad=self.y_labelpad)

        if len(y_lim) != 0:
            ax.set_ylim(y_lim)
        ax.grid(self.grid)

        ax.set_xticks(generation_list, labels=x_ticks)

        ax.get_yaxis().get_major_formatter().set_useOffset(False)
        for tick in ax.xaxis.get_major_ticks():
            tick.label1.set_fontsize(self.x_tick_fontsize)
        for tick in ax.yaxis.get_major_ticks():
            tick.label1.set_fontsize(self.y_tick_fontsize)

        fig_name = self.add_suffix_if_exist(self.trainer_env_var_across_scenarios_prefix, fig_suffix)
        self.save_fig(figure, fig_name)





























