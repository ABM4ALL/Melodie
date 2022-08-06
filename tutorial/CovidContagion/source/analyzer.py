import os

import matplotlib.pyplot as plt
import numpy as np

from Melodie import Config
from Melodie import db


class CovidAnalyzer:
    def __init__(self, config: "Config"):
        self.fig_folder = config.output_folder
        self.db = db.create_db_conn(config)

    def save_fig(self, fig, fig_name):
        fig.savefig(
            os.path.join(self.fig_folder, fig_name + ".png"),
            dpi=200,
            format="PNG",
        )
        plt.close(fig)

    def plot_health_state_share(self, scenario_id: int = 0, run_id: int = 0):
        df = self.db.read_dataframe("env_result")
        df = df.loc[(df["scenario_id"] == scenario_id) & (df["run_id"] == run_id)]
        values_dict = {
            "Not-infected": df["s0"],
            "Infected": df["s1"],
            "Recovered": df["s2"],
            "Dead": df["s3"],
            "Vaccinated": df["s4"],
        }

        figure = plt.figure(figsize=(12, 6))
        ax = figure.add_axes((0.1, 0.1, 0.8, 0.8))
        ax.set_xlabel("Period", fontsize=15)
        ax.set_ylabel("Count", fontsize=15)
        x = [i for i in range(0, len(list(values_dict.values())[0]))]
        bottom = np.zeros(len(x))
        for key, values in values_dict.items():
            ax.bar(
                x,
                values,
                bottom=bottom,
                label=key,
            )
            bottom += values
        ax.legend(fontsize=12)
        self.save_fig(figure, f"PopulationInfection_S{scenario_id}R{run_id}")

