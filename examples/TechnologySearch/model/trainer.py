
from Melodie import Trainer, GeneticAlgorithmTrainer
from .agent import TechnologySearchAgent


class TechnologySearchTrainer(Trainer):

    # def setup_agent_training_groups(self):
    #
    #     self.add_agent_group(group_name="wolf_list",
    #                          strategy_params=['strategy_param_1',
    #                                           'strategy_param_2',
    #                                           'strategy_param_3'],
    #                          fitness_func=self.wolf_list_fitness,
    #                          training_algorithm=GeneticAlgorithmTrainer)
    #
    #     self.add_agent_group(group_name="sheep_list",
    #                          strategy_params=['strategy_param_1',
    #                                           'strategy_param_2',
    #                                           'strategy_param_3'],
    #                          fitness_func=self.sheep_list_fitness,
    #                          training_algorithm=GeneticAlgorithmTrainer)
    #
    # def wolf_list_fitness(self, wolf: WolfAgent):
    #     return wolf.account
    #
    # def sheep_list_fitness(self, sheep: SheepAgent):
    #     return sheep.account


    # def setup_trainer_data_collector(self):
    #
    #     self.add_agent_result_property('agent_list', 'sleep_count')
    #     self.add_agent_result_property('agent_list', 'exploration_count')
    #     self.add_agent_result_property('agent_list', 'exploitation_count')
    #     self.add_agent_result_property('agent_list', 'imitation_count')
    #
    #     self.add_environment_result_property("average_technology")
    #     self.add_environment_result_property("average_account")
    #     self.add_environment_result_property("sleep_accumulated_share")
    #     self.add_environment_result_property("exploration_accumulated_share")
    #     self.add_environment_result_property("exploitation_accumulated_share")
    #     self.add_environment_result_property("imitation_accumulated_share")


    def setup(self):
        self.container_name = "agent_list"
        self.add_agent_training_property('agent_list', 'strategy_param_1')
        self.add_agent_training_property('agent_list', 'strategy_param_2')
        self.add_agent_training_property('agent_list', 'strategy_param_3')

        self.add_agent_result_property('agent_list', 'sleep_count')
        self.add_agent_result_property('agent_list', 'exploration_count')
        self.add_agent_result_property('agent_list', 'exploitation_count')
        self.add_agent_result_property('agent_list', 'imitation_count')

        self.add_environment_result_property("average_technology")
        self.add_environment_result_property("average_account")
        self.add_environment_result_property("sleep_accumulated_share")
        self.add_environment_result_property("exploration_accumulated_share")
        self.add_environment_result_property("exploitation_accumulated_share")
        self.add_environment_result_property("imitation_accumulated_share")

        self.save_env_trainer_result = True
        self.save_agent_trainer_result = True
        self.algorithm_cls = GeneticAlgorithmTrainer

    def fitness_agent(self, agent: TechnologySearchAgent):
        return agent.account
