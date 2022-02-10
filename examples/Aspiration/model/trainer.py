import numpy as np
import sqlalchemy

from Melodie import Trainer, GeneticAlgorithm
from .agent import AspirationAgent
from .scenario import AspirationScenario


class AspirationTrainer(Trainer):

    def setup(self):
        self.container_name = "agent_list"
        self.add_property('agent_list', 'strategy_param_1')
        self.add_property('agent_list', 'strategy_param_2')
        self.add_property('agent_list', 'strategy_param_3')

        # self.agent_trainer_result_save = True
        # self.env_trainer_result_save = True

        # self.add_agent_training_property('agent_list', 'strategy_param_1')
        # self.add_agent_training_property('agent_list', 'strategy_param_2')
        # self.add_agent_training_property('agent_list', 'strategy_param_3')
        # self.add_agent_result_property('agent_list', 'exploration_count')
        # self.add_environment_result_property("average_technology")

        self.environment_properties = ["average_technology",
                                       "sleep_accumulated_share",
                                       "exploration_accumulated_share",
                                       "exploitation_accumulated_share",
                                       "imitation_accumulated_share"]
        self.algorithm_cls = GeneticAlgorithm

    def fitness_agent(self, agent: AspirationAgent):
        return agent.account
