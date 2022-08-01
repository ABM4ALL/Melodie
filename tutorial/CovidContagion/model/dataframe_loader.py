import numpy as np
import sqlalchemy
from Melodie import DataFrameLoader
from model.scenario import CovidScenario
from model import dataframe_info


class CovidDataFrameLoader(DataFrameLoader):
    def setup(self):
        self.load_df(dataframe_info.simulator_scenarios)

    def register_generated_dataframes(self):
        def init_condition(initial_infected_percentage: float):
            condition = 0
            rand = np.random.uniform(0, 1)
            if rand <= initial_infected_percentage:
                condition = 1
            else:
                pass
            return condition

        with self.table_generator(
            "agent_params", lambda scenario: scenario.agent_num
        ) as g:

            def generator_func(scenario: "CovidScenario"):
                return {
                    "id": g.increment(),
                    "x": np.random.randint(0, scenario.grid_x_size),
                    "y": np.random.randint(0, scenario.grid_y_size),
                    "condition": init_condition(scenario.initial_infected_percentage),
                }

            g.set_row_generator(generator_func)
            g.set_column_data_types(
                {
                    "id": sqlalchemy.Integer(),
                    "x": sqlalchemy.Integer(),
                    "y": sqlalchemy.Integer(),
                    "condition": sqlalchemy.Integer(),
                }
            )
