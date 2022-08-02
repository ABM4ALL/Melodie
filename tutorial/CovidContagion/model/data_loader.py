from typing import TYPE_CHECKING
import numpy as np
from Melodie import DataLoader
from tutorial.CovidContagion.model import data_info as df_info

if TYPE_CHECKING:
    from .scenario import CovidScenario


class CovidDataLoader(DataLoader):
    def setup(self):
        self.load_dataframe(df_info.simulator_scenarios)
        self.load_dataframe(df_info.id_age_group)
        self.load_dataframe(df_info.id_health_state)
        self.load_dataframe(df_info.id_network_type)
        self.load_matrix(df_info.grid_stay_prob)
        self.generate_dataframe()

    @staticmethod
    def init_age_group(young_percentage: float):
        age_group = 0
        rand = np.random.uniform(0, 1)
        if rand <= young_percentage:
            pass
        else:
            age_group = 1
        return age_group

    @staticmethod
    def init_health_state(initial_infected_percentage: float):
        state = 0
        rand = np.random.uniform(0, 1)
        if rand <= initial_infected_percentage:
            state = 1
        else:
            pass
        return state

    @staticmethod
    def init_vaccination_trust(vaccination_trust_percentage: float):
        vaccination_trust_state = 0
        rand = np.random.uniform(0, 1)
        if rand <= vaccination_trust_percentage:
            vaccination_trust_state = 1
        else:
            pass
        return vaccination_trust_state

    def generate_dataframe(self):

        with self.dataframe_generator(
            df_info.agent_params.df_name, lambda scenario: scenario.agent_num
        ) as g:

            def generator_func(scenario: "CovidScenario"):
                return {
                    "id": g.increment(),
                    "x": np.random.randint(0, scenario.grid_x_size),
                    "y": np.random.randint(0, scenario.grid_y_size),
                    "age_group": self.init_age_group(scenario.young_percentage),
                    "health_state": self.init_health_state(
                        scenario.initial_infected_percentage
                    ),
                    "vaccination_trust_state": self.init_vaccination_trust(
                        scenario.vaccination_trust_percentage
                    ),
                }

            g.set_row_generator(generator_func)
            g.set_column_data_types(df_info.agent_params.columns)