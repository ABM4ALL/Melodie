
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict
import seaborn as sns
import matplotlib.pyplot as plt

from .config import Config

class Plotter(ABC):

    def __init__(self, config: Config):
        self.fig_folder = config.output_folder
        self.setup_common_fig_params()
        self.setup_trainer_agent_strategy_params_cov_heatmap_fig_params()
        self.setup_trainer_agent_strategy_params_cov_lines_fig_params()
        self.setup_trainer_agent_var_scatter_fig_params()
        self.setup_trainer_env_var_fig_params()
        self.setup_colors()
        self.setup()

    def setup_common_fig_params(self):
        self.fig_format = "PNG"
        self.fig_dpi = 200

    def setup_trainer_agent_strategy_params_cov_heatmap_fig_params(self):
        self.trainer_agent_strategy_params_cov_heatmap_fig_name_prefix = "trainer_agent_strategy_params_cov_heatmap_"
        self.trainer_agent_strategy_params_cov_heatmap_fig_size = (20, 3)
        self.trainer_agent_strategy_params_cov_heatmap_fig_axe_area = (0.05, 0.2, 0.94, 0.7)
        self.trainer_agent_strategy_params_cov_heatmap_title_fontsize = 16
        self.trainer_agent_strategy_params_cov_heatmap_title_pad = 10
        self.trainer_agent_strategy_params_cov_heatmap_x_label = "Agent"
        self.trainer_agent_strategy_params_cov_heatmap_x_label_fontsize = 15
        self.trainer_agent_strategy_params_cov_heatmap_x_labelpad = 10
        self.trainer_agent_strategy_params_cov_heatmap_y_label = "Strategy Parameter"
        self.trainer_agent_strategy_params_cov_heatmap_y_label_fontsize = 15
        self.trainer_agent_strategy_params_cov_heatmap_y_labelpad = 10
        self.trainer_agent_strategy_params_cov_heatmap_x_tick_fontsize = 10
        self.trainer_agent_strategy_params_cov_heatmap_y_tick_fontsize = 10

    def setup_trainer_agent_strategy_params_cov_lines_fig_params(self):
        self.trainer_agent_strategy_params_cov_lines_fig_name_prefix = "trainer_agent_strategy_params_cov_lines_"
        self.trainer_agent_strategy_params_cov_lines_fig_size = (12, 6)
        self.trainer_agent_strategy_params_cov_lines_fig_axe_area = (0.1, 0.15, 0.8, 0.75)
        self.trainer_agent_strategy_params_cov_lines_title_fontsize = 16
        self.trainer_agent_strategy_params_cov_lines_title_pad = 10
        self.trainer_agent_strategy_params_cov_lines_individual_line_width = 0.2
        self.trainer_agent_strategy_params_cov_lines_individual_line_alpha = 0.2
        self.trainer_agent_strategy_params_cov_lines_individual_line_style = '-'
        self.trainer_agent_strategy_params_cov_lines_average_line_width = 1
        self.trainer_agent_strategy_params_cov_lines_average_line_style = '-'
        self.trainer_agent_strategy_params_cov_lines_x_label = "Generation"
        self.trainer_agent_strategy_params_cov_lines_x_label_fontsize = 15
        self.trainer_agent_strategy_params_cov_lines_x_labelpad = 10
        self.trainer_agent_strategy_params_cov_lines_y_label = "Strategy Parameter Value"
        self.trainer_agent_strategy_params_cov_lines_y_label_fontsize = 15
        self.trainer_agent_strategy_params_cov_lines_y_labelpad = 10
        self.trainer_agent_strategy_params_cov_lines_x_tick_fontsize = 15
        self.trainer_agent_strategy_params_cov_lines_y_tick_fontsize = 15

    def setup_trainer_agent_var_scatter_fig_params(self):
        self.trainer_agent_var_scatter_fig_name_prefix = "trainer_agent_var_scatter_"
        self.trainer_agent_var_scatter_fig_size = (6, 6)
        self.trainer_agent_var_scatter_fig_axe_area = (0.15, 0.15, 0.8, 0.8)
        self.trainer_agent_var_scatter_area = 10
        self.trainer_agent_var_scatter_title_fontsize = 16
        self.trainer_agent_var_scatter_title_pad = 10
        self.trainer_agent_var_scatter_var_label_fontsize = 15
        self.trainer_agent_var_scatter_var_labelpad = 10
        self.trainer_agent_var_scatter_grid = True
        self.trainer_agent_var_scatter_tick_fontsize = 15

    def setup_trainer_env_var_fig_params(self):
        self.fig_name_prefix_trainer_env = "trainer_env_"
        self.trainer_env_var_cov_range_width = 1
        self.trainer_env_var_fig_size = (12, 6)
        self.trainer_env_var_fig_axe_area = (0.1, 0.15, 0.8, 0.75)
        self.trainer_env_var_title_fontsize = 16
        self.trainer_env_var_title_pad = 10
        self.trainer_env_var_x_label = "Generation"
        self.trainer_env_var_x_label_fontsize = 15
        self.trainer_env_var_x_labelpad = 10
        self.trainer_env_var_y_label_fontsize = 15
        self.trainer_env_var_y_labelpad = 10
        self.trainer_env_var_mean_linewidth = 3
        self.trainer_env_var_mean_linestyle = '-'
        self.trainer_env_var_cov_alpha = 0.3
        self.trainer_env_var_x_lim = None
        self.trainer_env_var_grid = True
        self.trainer_env_var_x_tick_fontsize = 15
        self.trainer_env_var_y_tick_fontsize = 15

    def setup_colors(self):
        self.colors = ["tab:orange", "tab:blue", "tab:green", "tab:red", "tab:purple",
                       "tab:brown", "tab:pink", "tab:gray", "tab:olive", "tab:cyan",
                       "dimgray", "lightcoral", "tomato", "peru", "darkorange", "gold",
                       "olivedrab", "lime", "darkslategrey", "royalblue", "violet",
                       "navy", "crimson"]

    def setup(self):
        pass

    def check_param(self, param, default_value):
        if param == None:
            value = default_value
        else:
            value = param
        return value

    def save_fig(self, fig, fig_name):
        fig.savefig(self.fig_folder + "/" + fig_name + ".png", dpi=self.fig_dpi, format=self.fig_format)
        plt.close(fig)

    def trainer_agent_strategy_params_cov_heatmap(self,
                                                  strategy_params_cov_matrix: np.ndarray,
                                                  fig_scenario: str,
                                                  strategy_params_ticks: list = None):

        figure = plt.figure(figsize=self.trainer_agent_strategy_params_cov_heatmap_fig_size,
                            dpi=self.fig_dpi, frameon=False)
        ax = figure.add_axes(self.trainer_agent_strategy_params_cov_heatmap_fig_axe_area)

        x_ticks = [i + 1 for i in range(0, strategy_params_cov_matrix.shape[1])]
        y_ticks = [i + 1 for i in range(0, strategy_params_cov_matrix.shape[0])]
        if strategy_params_ticks != None: y_ticks = strategy_params_ticks
        ax = sns.heatmap(strategy_params_cov_matrix, vmin=0, vmax=1,
                         xticklabels=x_ticks, yticklabels=y_ticks)

        ax.set_xlabel(self.trainer_agent_strategy_params_cov_heatmap_x_label,
                      fontsize=self.trainer_agent_strategy_params_cov_heatmap_x_label_fontsize,
                      labelpad=self.trainer_agent_strategy_params_cov_heatmap_x_labelpad)
        ax.set_ylabel(self.trainer_agent_strategy_params_cov_heatmap_y_label,
                      fontsize=self.trainer_agent_strategy_params_cov_heatmap_y_label_fontsize,
                      labelpad=self.trainer_agent_strategy_params_cov_heatmap_y_labelpad)

        plt.xticks(rotation=0.00001)
        plt.yticks(rotation=0.00001)

        for tick in ax.xaxis.get_major_ticks():
            tick.label1.set_fontsize(self.trainer_agent_strategy_params_cov_heatmap_x_tick_fontsize)
        for tick in ax.yaxis.get_major_ticks():
            tick.label1.set_fontsize(self.trainer_agent_strategy_params_cov_heatmap_y_tick_fontsize)

        fig_name = self.trainer_agent_strategy_params_cov_heatmap_fig_name_prefix + fig_scenario
        self.save_fig(figure, fig_name)

    def trainer_agent_strategy_params_cov_lines(self,
                                                strategy_params_agent_generation_matrix_dict: Dict[str, np.ndarray],
                                                fig_scenario: str,
                                                strategy_params_legend_dict: dict = None):

        figure = plt.figure(figsize=self.trainer_agent_strategy_params_cov_lines_fig_size,
                            dpi=self.fig_dpi, frameon=False)
        ax = figure.add_axes(self.trainer_agent_strategy_params_cov_lines_fig_axe_area)

        color_counter = 0
        for strategy_param, agent_generation_matrix in strategy_params_agent_generation_matrix_dict.items():
            # for agent_id in range(0, agent_generation_matrix.shape[0]):
            #     strategy_param_cov = agent_generation_matrix[agent_id]
            #     ax.plot(generation_list, strategy_param_cov,
            #             linewidth=self.trainer_agent_strategy_params_cov_lines_individual_line_width,
            #             linestyle=self.trainer_agent_strategy_params_cov_lines_individual_line_style,
            #             color=self.colors[color_counter],
            #             alpha=self.trainer_agent_strategy_params_cov_lines_individual_line_alpha)
            average_strategy_param_cov = agent_generation_matrix.mean(axis=0)
            generation_list = list(range(len(average_strategy_param_cov)))
            ax.plot(generation_list, average_strategy_param_cov,
                    linewidth=self.trainer_agent_strategy_params_cov_lines_average_line_width,
                    linestyle=self.trainer_agent_strategy_params_cov_lines_average_line_style,
                    color=self.colors[color_counter],
                    label=strategy_params_legend_dict[strategy_param])
            color_counter += 1

        if len(strategy_params_legend_dict) > 1:
            figure.legend(fontsize=15, bbox_to_anchor=(0, 1.02, 1, 0.1), bbox_transform=ax.transAxes,
                          loc='lower left', ncol=3, borderaxespad=0, mode='expand', frameon=True)

        ax.set_xlabel(self.trainer_agent_strategy_params_cov_lines_x_label,
                      fontsize=self.trainer_agent_strategy_params_cov_lines_x_label_fontsize,
                      labelpad=self.trainer_agent_strategy_params_cov_lines_x_labelpad)
        ax.set_ylabel(self.trainer_agent_strategy_params_cov_lines_y_label,
                      fontsize=self.trainer_agent_strategy_params_cov_lines_y_label_fontsize,
                      labelpad=self.trainer_agent_strategy_params_cov_lines_y_labelpad)

        for tick in ax.xaxis.get_major_ticks():
            tick.label1.set_fontsize(self.trainer_agent_strategy_params_cov_lines_x_tick_fontsize)
        for tick in ax.yaxis.get_major_ticks():
            tick.label1.set_fontsize(self.trainer_agent_strategy_params_cov_lines_y_tick_fontsize)

        fig_name = self.trainer_agent_strategy_params_cov_lines_fig_name_prefix + fig_scenario
        self.save_fig(figure, fig_name)

    def trainer_agent_var_scatter(self,
                                  var_1_name, var_1_value,
                                  var_2_name, var_2_value,
                                  fig_scenario,
                                  area_value=None,
                                  var_1_lim=None, var_2_lim=None,
                                  var_1_label=None, var_2_label=None,
                                  fig_title=None):

        figure = plt.figure(figsize=self.trainer_agent_var_scatter_fig_size, dpi=self.fig_dpi, frameon=False)
        ax = figure.add_axes(self.trainer_agent_var_scatter_fig_axe_area)

        if area_value == None:
            area = self.trainer_agent_var_scatter_area
        else:
            area = area_value
        ax.scatter(var_1_value, var_2_value, s=area, c=self.colors[0], alpha=0.5)

        if fig_title != None:
            ax.set_title(fig_title,
                         fontsize=self.trainer_agent_var_scatter_title_fontsize,
                         pad=self.trainer_agent_var_scatter_title_pad)
        ax.set_xlabel(self.check_param(var_1_label, var_1_name),
                      fontsize=self.trainer_agent_var_scatter_var_label_fontsize,
                      labelpad=self.trainer_agent_var_scatter_var_labelpad)
        ax.set_ylabel(self.check_param(var_2_label, var_2_name),
                      fontsize=self.trainer_agent_var_scatter_var_label_fontsize,
                      labelpad=self.trainer_agent_var_scatter_var_labelpad)

        if var_1_lim != None: ax.set_xlim(var_1_lim)
        if var_2_lim != None: ax.set_ylim(var_2_lim)
        ax.grid(self.trainer_agent_var_scatter_grid)

        ax.get_yaxis().get_major_formatter().set_useOffset(False)
        for tick in ax.xaxis.get_major_ticks():
            tick.label1.set_fontsize(self.trainer_agent_var_scatter_tick_fontsize)
        for tick in ax.yaxis.get_major_ticks():
            tick.label1.set_fontsize(self.trainer_agent_var_scatter_tick_fontsize)

        fig_name = self.fig_name_prefix_trainer_env + fig_scenario + var_1_name + "_" + var_2_name
        self.save_fig(figure, fig_name)

    def trainer_env_var(self, var_name, var_value_dict, fig_scenario,
                        fig_title=None, y_label=None, y_lim=None):

        figure = plt.figure(figsize=self.trainer_env_var_fig_size, dpi=self.fig_dpi, frameon=False)
        ax = figure.add_axes(self.trainer_env_var_fig_axe_area)

        color_counter = 0
        for key, value in var_value_dict.items():
            path_name = key
            path_var_mean = value[0]
            path_var_cov = value[1]
            generation_list = list(range(len(path_var_mean)))
            ax.plot(generation_list, path_var_mean,
                    linewidth=self.trainer_env_var_mean_linewidth,
                    linestyle=self.trainer_env_var_mean_linestyle,
                    color=self.colors[color_counter],
                    label=path_name)
            ax.fill_between(generation_list,
                            path_var_mean * (1 - self.trainer_env_var_cov_range_width * path_var_cov),
                            path_var_mean * (1 + self.trainer_env_var_cov_range_width * path_var_cov),
                            alpha=self.trainer_env_var_cov_alpha, facecolor=self.colors[color_counter])
            color_counter += 1
            if color_counter == len(self.colors):
                color_counter = np.random.randint(0, len(self.colors))
        if fig_title != None:
            ax.set_title(fig_title, fontsize=self.trainer_env_var_title_fontsize, pad=self.trainer_env_var_title_pad)
        ax.set_ylabel(self.check_param(y_label, var_name),
                      fontsize=self.trainer_env_var_x_label_fontsize,
                      labelpad=self.trainer_env_var_x_labelpad)
        ax.set_xlabel(self.trainer_env_var_x_label,
                      fontsize=self.trainer_env_var_y_label_fontsize,
                      labelpad=self.trainer_env_var_y_labelpad)
        if self.trainer_env_var_x_lim != None: ax.set_xlim(self.trainer_env_var_x_lim)
        if y_lim != None: ax.set_ylim(y_lim)
        ax.grid(self.trainer_env_var_grid)

        if len(var_value_dict) > 1:
            figure.legend(fontsize=15, bbox_to_anchor=(0, 1.02, 1, 0.1), bbox_transform=ax.transAxes,
                          loc='lower left', ncol=2, borderaxespad=0, mode='expand', frameon=True)

        ax.get_yaxis().get_major_formatter().set_useOffset(False)
        for tick in ax.xaxis.get_major_ticks():
            tick.label1.set_fontsize(self.trainer_env_var_x_tick_fontsize)
        for tick in ax.yaxis.get_major_ticks():
            tick.label1.set_fontsize(self.trainer_env_var_y_tick_fontsize)

        fig_name = self.fig_name_prefix_trainer_env + fig_scenario + var_name
        self.save_fig(figure, fig_name)
