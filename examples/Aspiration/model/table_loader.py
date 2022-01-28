import numpy as np
import sqlalchemy

from Melodie import DataFrameLoader
from .scenario import AspirationScenario


class AspirationDataFrameLoader(DataFrameLoader):
    def register_scenario_dataframe(self):
        scenarios_dict = {"periods": sqlalchemy.Integer(),
                          "agent_num": sqlalchemy.Integer(),
                          "market_strategy": sqlalchemy.Integer(),
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
                          "imitation_success_rate": sqlalchemy.Float()}

        self.load_dataframe('simulator_scenarios', 'simulator_scenarios.xlsx', scenarios_dict)

        self.load_dataframe('trainer_scenarios', 'trainer_scenarios.xlsx', scenarios_dict)
        self.load_dataframe('trainer_params_scenarios', 'trainer_params_scenarios.xlsx', {})

    def register_static_dataframes(self) -> None:
        # load由trainer得到的表
        pass

    def register_generated_dataframes(self):
        with self.new_table_generator('agent_params', lambda scenario: scenario.agent_num) as g:
            def generator_func(scenario: 'AspirationScenario'):
                return {'id': g.increment(),
                        'technology': scenario.initial_technology,
                        'aspiration_level': scenario.initial_technology + scenario.market_profit_mean,
                        'aspiration_update_strategy': scenario.aspiration_update_strategy,
                        'historical_aspiration_update_param': scenario.historical_aspiration_update_param,
                        'social_aspiration_update_param': scenario.social_aspiration_update_param,
                        'profit': 0.0,
                        'account': 0.0,
                        'profit_aspiration_difference': 0.0,
                        'strategy_param_1': np.random.uniform(0, 100),  # 待改：应该是从trainer生成的表里读出来
                        'strategy_param_2': np.random.uniform(0, 100),  # 待改：应该是从trainer生成的表里读出来
                        'strategy_param_3': np.random.uniform(0, 100),  # 待改：应该是从trainer生成的表里读出来
                        'sleep_count': 0,
                        'exploration_count': 0,
                        'exploitation_count': 0,
                        'imitation_count': 0}

            g.set_row_generator(generator_func)
            g.set_column_data_types({'id': sqlalchemy.Integer(),
                                     'technology': sqlalchemy.Float(),
                                     'aspiration_level': sqlalchemy.Float(),
                                     'aspiration_update_strategy': sqlalchemy.Integer(),
                                     'historical_aspiration_update_param': sqlalchemy.Float(),
                                     'social_aspiration_update_param': sqlalchemy.Float(),
                                     'profit': sqlalchemy.Float(),
                                     'account': sqlalchemy.Float(),
                                     'profit_aspiration_difference': sqlalchemy.Float(),
                                     'strategy_param_1': sqlalchemy.Float(),
                                     'strategy_param_2': sqlalchemy.Float(),
                                     'strategy_param_3': sqlalchemy.Float(),
                                     'sleep_count': sqlalchemy.Integer(),
                                     'exploration_count': sqlalchemy.Integer(),
                                     'exploitation_count': sqlalchemy.Integer(),
                                     'imitation_count': sqlalchemy.Integer()})
