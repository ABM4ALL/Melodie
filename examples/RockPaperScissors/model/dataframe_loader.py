import numpy as np
import sqlalchemy

from Melodie import DataFrameLoader
from .scenario import RPSScenario


class RPSDataFrameLoader(DataFrameLoader):
    def register_scenario_dataframe(self):
        scenario_data_type_dict = {
            "number_of_run": sqlalchemy.Integer(),
            "periods": sqlalchemy.Integer(),
            "agent_num": sqlalchemy.Integer(),
            "payoff_win_min": sqlalchemy.Float(),
            "payoff_win_max": sqlalchemy.Float(),
            "payoff_lose_min": sqlalchemy.Integer(),
            "payoff_lose_max": sqlalchemy.Float(),
            "payoff_tie": sqlalchemy.Float(),
            "number_of_path": sqlalchemy.Integer(),
            "number_of_generation": sqlalchemy.Integer(),
            "strategy_population": sqlalchemy.Integer(),
            "mutation_prob": sqlalchemy.Float(),
            "strategy_param_code_length": sqlalchemy.Integer(),
            "strategy_param_1_min": sqlalchemy.Float(),
            "strategy_param_1_max": sqlalchemy.Float(),
            "strategy_param_2_min": sqlalchemy.Float(),
            "strategy_param_2_max": sqlalchemy.Float(),
            "strategy_param_3_min": sqlalchemy.Float(),
            "strategy_param_3_max": sqlalchemy.Float(),
        }

        self.load_dataframe(
            "simulator_scenarios", "simulator_scenarios.xlsx", scenario_data_type_dict
        )
        self.load_dataframe(
            "trainer_scenarios", "trainer_scenarios.xlsx", scenario_data_type_dict
        )
        self.load_dataframe(
            "trainer_params_scenarios",
            "trainer_params_scenarios.xlsx",
            scenario_data_type_dict,
        )

    def generate_dataframe(self):
        with self.dataframe_generator(
            "agent_params", lambda scenario: scenario.agent_num
        ) as g:

            def generator_func(scenario: "RPSScenario"):
                return {
                    "id": g.increment(),
                    "payoff_rock_win": np.random.uniform(
                        scenario.payoff_win_min, scenario.payoff_win_max
                    ),
                    "payoff_rock_lose": np.random.uniform(
                        scenario.payoff_lose_min, scenario.payoff_lose_max
                    ),
                    "payoff_paper_win": np.random.uniform(
                        scenario.payoff_win_min, scenario.payoff_win_max
                    ),
                    "payoff_paper_lose": np.random.uniform(
                        scenario.payoff_lose_min, scenario.payoff_lose_max
                    ),
                    "payoff_scissors_win": np.random.uniform(
                        scenario.payoff_win_min, scenario.payoff_win_max
                    ),
                    "payoff_scissors_lose": np.random.uniform(
                        scenario.payoff_lose_min, scenario.payoff_lose_max
                    ),
                    "payoff_tie": scenario.payoff_tie,
                    "strategy_param_1": np.random.uniform(0, 100),
                    "strategy_param_2": np.random.uniform(0, 100),
                    "strategy_param_3": np.random.uniform(0, 100),
                }

            g.set_row_generator(generator_func)
            g.set_column_data_types(
                {
                    "id": sqlalchemy.Integer(),
                    "payoff_rock_win": sqlalchemy.Float(),
                    "payoff_rock_lose": sqlalchemy.Float(),
                    "payoff_paper_win": sqlalchemy.Float(),
                    "payoff_paper_lose": sqlalchemy.Float(),
                    "payoff_scissors_win": sqlalchemy.Float(),
                    "payoff_scissors_lose": sqlalchemy.Float(),
                    "payoff_tie": sqlalchemy.Float(),
                    "strategy_param_1": sqlalchemy.Float(),
                    "strategy_param_2": sqlalchemy.Float(),
                    "strategy_param_3": sqlalchemy.Float(),
                }
            )
