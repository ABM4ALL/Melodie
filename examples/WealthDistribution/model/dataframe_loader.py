import sqlalchemy

from Melodie import DataLoader
from .scenario import GiniScenario


class GiniDataframeLoader(DataLoader):
    def register_scenario_dataframe(self):
        scenarios_dict = {}
        self.load_dataframe(
            "simulator_scenarios", "simulator_scenarios.xlsx", scenarios_dict
        )

    def generate_dataframe(self):

        with self.dataframe_generator(
            "agent_params", lambda scenario: scenario.agent_num
        ) as g:

            def generator_func(scenario: GiniScenario):
                return {
                    "id": g.increment(),
                    "productivity": scenario.agent_productivity,
                    "account": 0.0,
                }

            g.set_row_generator(generator_func)
            g.set_column_data_types(
                {
                    "id": sqlalchemy.Integer(),
                    "productivity": sqlalchemy.Float(),
                    "account": sqlalchemy.Float(),
                }
            )
