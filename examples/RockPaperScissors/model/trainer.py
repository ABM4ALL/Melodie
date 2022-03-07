
from Melodie import Trainer, GeneticAlgorithmTrainer
from .agent import RPSAgent


class RPSTrainer(Trainer):

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

    def fitness_agent(self, agent: RPSAgent):
        return agent.account
