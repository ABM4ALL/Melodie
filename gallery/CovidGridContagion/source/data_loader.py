from typing import TYPE_CHECKING

import numpy as np

from tutorial.CovidContagion.source.data_loader import CovidDataLoader
from . import data_info

if TYPE_CHECKING:
    from .scenario import CovidGridScenario


class CovidGridDataLoader(CovidDataLoader):
    def setup(self):
        self.load_dataframe(data_info.simulator_scenarios)
        self.load_dataframe(data_info.id_age_group)
        self.load_dataframe(data_info.id_health_state)
        self.load_matrix(data_info.grid_stay_prob)
        self.generate_agent_dataframe()

    def generate_agent_dataframe(self):
        with self.dataframe_generator(
            data_info.agent_params, lambda scenario: scenario.agent_num
        ) as g:

            def generator_func(scenario: "CovidGridScenario"):
                return {
                    "id": g.increment(),
                    "x": np.random.randint(0, scenario.grid_x_size),
                    "y": np.random.randint(0, scenario.grid_y_size),
                    "age_group": self.init_age_group(scenario),
                    "health_state": self.init_health_state(scenario),
                }

            g.set_row_generator(generator_func)
