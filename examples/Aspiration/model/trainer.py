import numpy as np
import sqlalchemy

from Melodie import Trainer, GeneticAlgorithm
from .agent import AspirationAgent
from .scenario import AspirationScenario


class AspirationTrainer(Trainer):

    def setup(self):
        self.container_name = "agent_list"
        self.add_agent_training_property('agent_list', 'strategy_param_1')
        self.add_agent_training_property('agent_list', 'strategy_param_2')
        self.add_agent_training_property('agent_list', 'strategy_param_3')
        self.save_env_trainer_result = True
        self.save_agent_trainer_result = True
        self.add_agent_result_property('agent_list', 'exploration_count')

        self.add_environment_result_property("average_technology")
        self.add_environment_result_property("sleep_accumulated_share")
        self.add_environment_result_property("exploration_accumulated_share")
        self.add_environment_result_property("exploitation_accumulated_share")
        self.add_environment_result_property("imitation_accumulated_share")
        self.algorithm_cls = GeneticAlgorithm

    def fitness_agent(self, agent: AspirationAgent):
        return agent.account
