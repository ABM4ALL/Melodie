import sqlalchemy
import numpy as np
from Melodie import DataLoader

from .scenario import OpinionDynamicsScenario


class OpinionDynamicsDataframeLoader(DataLoader):
    def register_scenario_dataframe(self):
        scenarios_dict = {
            "id": sqlalchemy.Integer(),
            "run_num": sqlalchemy.Integer(),
            "period_num": sqlalchemy.Integer(),
            "agent_num": sqlalchemy.Integer(),
            "network_param_k": sqlalchemy.Integer(),
            "network_param_p": sqlalchemy.Float(),
            "opinion_level_min": sqlalchemy.Float(),
            "opinion_level_max": sqlalchemy.Float(),
            "opinion_radius_min": sqlalchemy.Float(),
            "opinion_radius_max": sqlalchemy.Float(),
            "communication_prob": sqlalchemy.Float(),
            "relative_agreement_param": sqlalchemy.Float(),
        }
        self.load_dataframe(
            "simulator_scenarios", "simulator_scenarios.xlsx", scenarios_dict
        )

    def generate_dataframe(self):
        with self.dataframe_generator(
            "agent_params", lambda scenario: scenario.agent_num
        ) as g:

            def generator_func(scenario: "OpinionDynamicsScenario"):
                return {
                    "id": g.increment(),
                    "opinion_level": np.random.uniform(
                        scenario.opinion_level_min, scenario.opinion_level_max
                    ),
                    "opinion_radius": np.random.uniform(
                        scenario.opinion_radius_min, scenario.opinion_radius_max
                    ),
                }

            g.set_row_generator(generator_func)
            g.set_column_data_types(
                {
                    "id": sqlalchemy.Integer(),
                    "opinion_level": sqlalchemy.Float(),
                    "opinion_radius": sqlalchemy.Float(),
                }
            )
