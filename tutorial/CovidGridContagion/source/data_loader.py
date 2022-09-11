from typing import TYPE_CHECKING

import numpy as np

from Melodie import DataLoader
from tutorial.CovidGridContagion.source import data_info

if TYPE_CHECKING:
    from .scenario import CovidScenario


class CovidDataLoader(DataLoader):
    def setup(self):
        self.load_dataframe(data_info.simulator_scenarios)
        self.load_dataframe(data_info.id_age_group)
        self.load_dataframe(data_info.id_health_state)
        self.load_matrix(data_info.grid_stay_prob)
        self.generate_agent_dataframe()

    @staticmethod
    def init_age_group(scenario: "CovidScenario"):
        age_group = 0
        if np.random.uniform(0, 1) > scenario.young_percentage:
            age_group = 1
        return age_group

    @staticmethod
    def init_health_state(scenario: "CovidScenario"):
        state = 0
        if np.random.uniform(0, 1) <= scenario.initial_infected_percentage:
            state = 1
        return state

    def generate_agent_dataframe(self):
        with self.dataframe_generator(data_info.agent_params, lambda scenario: scenario.agent_num) as g:
            def generator_func(scenario: "CovidScenario"):
                return {
                    "id": g.increment(),
                    "x": np.random.randint(0, scenario.grid_x_size),
                    "y": np.random.randint(0, scenario.grid_y_size),
                    "age_group": self.init_age_group(scenario),
                    "health_state": self.init_health_state(scenario),
                }
            g.set_row_generator(generator_func)
