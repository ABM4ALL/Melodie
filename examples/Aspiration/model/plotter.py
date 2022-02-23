
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

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

    def trainer_env_var_strategy_cost_heatmap(self,
                                              env_var_strategy_cost_matrix: np.ndarray,
                                              fig_name: str,
                                              imitation_cost_ticks: list,
                                              exploration_cost_ticks: list,
                                              v_min: float = None,
                                              v_max: float = None):

        figure = plt.figure(figsize=(6, 4.5),
                            dpi=self.fig_dpi, frameon=False)
        ax = figure.add_axes((0.15, 0.15, 0.8, 0.8))

        if v_min == None and v_max == None:
            ax = sns.heatmap(env_var_strategy_cost_matrix, annot=True, fmt="g", linewidths=.5,
                             xticklabels=imitation_cost_ticks, yticklabels=exploration_cost_ticks)
        else:
            ax = sns.heatmap(env_var_strategy_cost_matrix, annot=True, fmt="g", linewidths=.5,
                             xticklabels=imitation_cost_ticks, yticklabels=exploration_cost_ticks,
                             vmin=v_min, vmax=v_max)

        ax.set_xlabel("Imitation Cost",
                      fontsize=15,
                      labelpad=10)
        ax.set_ylabel("Exploration Cost",
                      fontsize=15,
                      labelpad=10)

        plt.xticks(rotation=0.00001)
        plt.yticks(rotation=0.00001)

        for tick in ax.xaxis.get_major_ticks():
            tick.label1.set_fontsize(15)
        for tick in ax.yaxis.get_major_ticks():
            tick.label1.set_fontsize(15)

        self.save_fig(figure, fig_name)













