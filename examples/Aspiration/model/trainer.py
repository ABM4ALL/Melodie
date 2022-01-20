import numpy as np
import sqlalchemy

from Melodie import Trainer
from Melodie.trainer import GeneticAlgorithm
from .agent import AspirationAgent
from examples.Aspiration.model.scenario import AspirationScenario


class AspirationTrainer(Trainer):

    # 能不能再多继承一个AspirationSimulator？这样就不用重新注册下面那些东西了？
    # 或者，把所有跟注册有关的东西都单独拎出来弄一个新class Register？这样simulator, trainer, calibrator就都简化了。

    # 这个目前还没实现是吧：针对不同的scenario和training_scenario组合，每个组合都train一次。
    # training相关的表还没注册。

    # 似乎scenario是更高一级的，在simulator和trainer之上注册的 --> @Zhanyi？

    # 总结一下需要保存哪些结果
    # 1. 各agent每generation的参数值
    # 2. 自动计算一些behavior parameter的COV变化
    # 3. 自动计算一些宏观变量的收敛路径——每generation都是一个区间，因为有20次模拟

    def setup(self):
        self.container_name = "agent_list"
        self.add_property('agent_list', 'strategy_param_1')
        self.add_property('agent_list', 'strategy_param_2')
        self.add_property('agent_list', 'strategy_param_3')
        self.environment_properties = ['average_technology']

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
        self.load_dataframe('scenarios', 'trainer_scenarios.xlsx', scenarios_dict)
        self.load_dataframe('learning_scenarios', 'trainer_params_scenarios.xlsx', {})

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

    def fitness_agent(self, agent: AspirationAgent):
        return agent.account
