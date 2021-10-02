# -*- coding: utf-8 -*-
__author__ = 'Songmin'

import os
import matplotlib.pyplot as plt

from Melodie.db import create_db_conn
from Melodie.run import get_config, current_scenario, get_run_id


class Analyzer:

    def analyze_AgentWealth(self, id_agent):
        # df[(df['实发工资'] > 1000) & (df['性别'] == '男')]
        scenario_id = current_scenario().id
        run_id = get_run_id()
        AgentResult = create_db_conn().query_agent_results()
        AgentWealth = \
            AgentResult.loc[(AgentResult["id"] == id_agent) &
                            (AgentResult['scenario_id'] == scenario_id) &
                            (AgentResult['run_id'] == run_id)]["account"].values
        self.plot_AgentWealth(AgentWealth, id_agent, get_config().output_folder, current_scenario().id)

        return None

    def analyze_WealthAndGini(self):
        scenario_id = current_scenario().id
        run_id = get_run_id()
        EnvironmentResult = create_db_conn().query_env_results()
        envs = EnvironmentResult.loc[(EnvironmentResult['run_id'] == run_id) &
                                     (EnvironmentResult['scenario_id'] == scenario_id)]
        TotalWealth = envs["total_wealth"].values
        Gini = envs["gini"].values
        self.plot_WealthAndGini(TotalWealth, Gini, get_config().output_folder, current_scenario().id)

        return None

    def plot_AgentWealth(self, agent_wealth_array, id_agent, figure_folder, id_scenario):

        figure = plt.figure(figsize=(12, 8), dpi=200, frameon=False)
        ax_1 = figure.add_axes([0.1, 0.1, 0.8, 0.8])

        ax_1.plot(range(0, len(agent_wealth_array)),
                  agent_wealth_array,
                  linewidth=3,
                  linestyle='-',
                  color="red",
                  label="AgentWealth")

        ax_1.set_xlabel("Periods", fontsize=25, labelpad=10)
        ax_1.set_ylabel("Wealth of Agent " + str(id_agent), fontsize=25, labelpad=10)

        for tick in ax_1.xaxis.get_major_ticks():
            tick.label1.set_fontsize(20)
        for tick in ax_1.yaxis.get_major_ticks():
            tick.label1.set_fontsize(20)

        fig_name = f"S_{id_scenario}_R_{get_run_id()}_WealthAgent_{id_agent}"
        figure.savefig(os.path.join(figure_folder, fig_name + ".png"), dpi=200, format='PNG')
        plt.close(figure)

    def plot_WealthAndGini(self, total_wealth_array, gini_array, figure_folder, id_scenario):

        figure = plt.figure(figsize=(12, 8), dpi=200, frameon=False)
        ax = figure.add_axes([0.15, 0.15, 0.7, 0.7])
        ax_2 = ax.twinx()
        x_pos = range(0, len(total_wealth_array))

        ax.plot(x_pos,
                total_wealth_array,
                linewidth=3,
                linestyle='-',
                color="red",
                label="Total Wealth")

        ax_2.plot(x_pos,
                  gini_array,
                  linewidth=3,
                  linestyle='-',
                  color="blue",
                  label="Gini Index")

        figure.legend(fontsize=15, bbox_to_anchor=(0, 1.02, 1, 0.1), bbox_transform=ax.transAxes,
                      loc='lower left', ncol=3, borderaxespad=0, mode='expand', frameon=True)
        ax.set_xlabel("Periods", fontsize=25, labelpad=10)
        ax.set_ylabel("Total wealth of agents", fontsize=25, labelpad=10)
        ax_2.set_ylabel("Gini index", fontsize=25, labelpad=10)

        for tick in ax.xaxis.get_major_ticks():
            tick.label1.set_fontsize(20)
        for tick in ax.yaxis.get_major_ticks():
            tick.label1.set_fontsize(20)
        for tick in ax_2.yaxis.get_major_ticks():
            tick.label2.set_fontsize(20)

        # fig_name = "S" + str(id_scenario) + "_WealthAndGini"
        fig_name = f"S_{id_scenario}_R_{get_run_id()}_WealthAndGini"
        figure.savefig(os.path.join(figure_folder, fig_name + ".png"), dpi=200, format='PNG')
        plt.close(figure)

    def run(self):
        self.analyze_AgentWealth(1)
        self.analyze_WealthAndGini()
