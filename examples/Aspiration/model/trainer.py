import numpy as np
import sqlalchemy

from Melodie import Trainer
from Melodie.trainer import GeneticAlgorithm
from examples.Aspiration.model.scenario import AspirationScenario


class AspirationTrainer(Trainer):
    # 针对不同的scenario和training_scenario组合，每个组合都train一次。
    # 似乎scenario是更高一级的，在simulator和trainer之上注册的。
    def setup(self):
        self.add_property('agent_list', 'strategy_param_1')
        self.add_property('agent_list', 'strategy_param_2')
        self.add_property('agent_list', 'strategy_param_3')
        genes = 10
        strategy_param_code_length = 10
        algorithm = GeneticAlgorithm(100, genes, 0.02, strategy_param_code_length)
        self.set_algorithm(algorithm)

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
        self.load_dataframe('scenarios', 'scenarios.xlsx', scenarios_dict)

    def register_static_dataframes(self) -> None:
        # load由trainer得到的表
        pass

    def register_generated_dataframes(self):
        with self.new_table_generator('agent_params', lambda scenario: scenario.agent_num) as g:
            def generator_func(scenario: AspirationScenario):
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

    # def loss(self, param1, param2, param3):
    #     return param1 + param2 + param3
    #
    # def fitness(self, loss):
    #     return loss
