import sqlalchemy

from Melodie import DataLoader, DataFrameInfo
from .scenario import GiniScenario


class GiniDataframeLoader(DataLoader):
    def setup(self):
        self.register_scenario_dataframe()
        self.generate_dataframe()

    def register_scenario_dataframe(self):
        scenarios_dict = {
            "trade_num": sqlalchemy.Integer(),
            "agent_num": sqlalchemy.Integer(),
            "agent_account_min": sqlalchemy.Float(),
            "agent_account_max": sqlalchemy.Float(),
            "id": sqlalchemy.Integer(),
            "rich_win_prob": sqlalchemy.Float(),
            "periods": sqlalchemy.Integer(),
            "number_of_run": sqlalchemy.Integer(),
            "agent_productivity": sqlalchemy.Integer(),
        }
        self.load_dataframe(
            DataFrameInfo(
                "simulator_scenarios", scenarios_dict, "simulator_scenarios.xlsx"
            )
        )

    def generate_dataframe(self):
        with self.dataframe_generator(
            DataFrameInfo(
                "agent_params",
                {
                    "id": sqlalchemy.Integer(),
                    "productivity": sqlalchemy.Float(),
                    "account": sqlalchemy.Float(),
                },
            ),
            lambda scenario: scenario.agent_num,
        ) as g:

            def generator_func(scenario: GiniScenario):
                return {
                    "id": g.increment(),
                    "productivity": scenario.agent_productivity,
                    "account": 0.0,
                }

            g.set_row_generator(generator_func)
