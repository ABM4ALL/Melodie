import numpy as np
import sqlalchemy

from Melodie import DataFrameLoader
from .scenario import RPSScenario


class RPSDataFrameLoader(DataFrameLoader):

    def register_scenario_dataframe(self):
        scenario_data_type_dict = {"number_of_run": sqlalchemy.Integer(),
                                   "periods": sqlalchemy.Integer(),
                                   "agent_num": sqlalchemy.Integer(),
                                   "market_profit_mean": sqlalchemy.Float(),
                                   "market_profit_sigma": sqlalchemy.Float(),
                                   "aspiration_update_strategy": sqlalchemy.Integer(),
                                   "historical_aspiration_update_param": sqlalchemy.Float(),
                                   "social_aspiration_update_param": sqlalchemy.Float(),
                                   "initial_technology": sqlalchemy.Float(),
                                   "sigma_exploitation": sqlalchemy.Float(),
                                   "mean_exploration": sqlalchemy.Float(),
                                   "sigma_exploration": sqlalchemy.Float(),
                                   "imitation_share": sqlalchemy.Float(),
                                   "imitation_fail_rate": sqlalchemy.Float(),
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
                                   "strategy_param_3_max": sqlalchemy.Float()}

        self.load_dataframe('simulator_scenarios', 'simulator_scenarios.xlsx', scenario_data_type_dict)
        self.load_dataframe('trainer_scenarios', 'trainer_scenarios.xlsx', scenario_data_type_dict)
        self.load_dataframe('trainer_params_scenarios', 'trainer_params_scenarios.xlsx', scenario_data_type_dict)

    def register_generated_dataframes(self):
        with self.table_generator('agent_params', lambda scenario: scenario.agent_num) as g:
            def generator_func(scenario: 'RPSScenario'):
                return {'id': g.increment(),
                        'technology': scenario.initial_technology,
                        'aspiration_level': scenario.initial_technology + scenario.market_profit_mean,
                        'aspiration_update_strategy': scenario.aspiration_update_strategy,
                        'historical_aspiration_update_param': scenario.historical_aspiration_update_param,
                        'social_aspiration_update_param': scenario.social_aspiration_update_param,
                        'strategy_param_1': np.random.uniform(0, 100),
                        'strategy_param_2': np.random.uniform(0, 100),
                        'strategy_param_3': np.random.uniform(0, 100)}

            g.set_row_generator(generator_func)
            g.set_column_data_types({'id': sqlalchemy.Integer(),
                                     'technology': sqlalchemy.Float(),
                                     'aspiration_level': sqlalchemy.Float(),
                                     'aspiration_update_strategy': sqlalchemy.Integer(),
                                     'historical_aspiration_update_param': sqlalchemy.Float(),
                                     'social_aspiration_update_param': sqlalchemy.Float(),
                                     'strategy_param_1': sqlalchemy.Float(),
                                     'strategy_param_2': sqlalchemy.Float(),
                                     'strategy_param_3': sqlalchemy.Float()})
