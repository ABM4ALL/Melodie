from typing import TYPE_CHECKING
import numpy as np
from Melodie import DataFrameLoader
from tutorial.CovidContagion.model import dataframe_info as df_info

if TYPE_CHECKING:
    from .scenario import CovidScenario


class CovidDataFrameLoader(DataFrameLoader):

    def setup(self):
        self.load_dataframe(df_info.simulator_scenarios)
        self.load_dataframe(df_info.id_age_group)
        self.load_dataframe(df_info.id_health_state)
        self.load_dataframe(df_info.id_network_type)

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

    def register_generated_dataframes(self):

        with self.table_generator(df_info.agent_params.df_name, lambda scenario: scenario.agent_num) as g:
            # table_generator的名字不好，改成dataframe_generator
            # Melodie里只有dataframe和grid的matrix
            # 参数也改成df_info, 下面set_column_data_types就自动内部实现了

            def generator_func(scenario: 'CovidScenario'):
                return {
                    "id": g.increment(),
                    "x": np.random.randint(0, scenario.grid_x_size),
                    "y": np.random.randint(0, scenario.grid_y_size),
                    "age_group": self.init_age_group(scenario.young_percentage),
                    "health_state": self.init_health_state(scenario.initial_infected_percentage),
                    "vaccination_trust_state": self.init_vaccination_trust(scenario.vaccination_trust_percentage)
                }

            g.set_row_generator(generator_func)
            g.set_column_data_types(df_info.agent_params.columns)


