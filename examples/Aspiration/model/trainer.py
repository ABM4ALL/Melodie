import numpy as np
import sqlalchemy

from Melodie import Trainer
from .agent import AspirationAgent
from .scenario import AspirationScenario


class AspirationTrainer(Trainer):

    def setup(self):
        self.container_name = "agent_list"
        self.add_property('agent_list', 'strategy_param_1')
        self.add_property('agent_list', 'strategy_param_2')
        self.add_property('agent_list', 'strategy_param_3')
        self.environment_properties = ["average_technology",
                                       "sleep_accumulated_share",
                                       "exploration_accumulated_share",
                                       "exploitation_accumulated_share",
                                       "imitation_accumulated_share"]

    def fitness_agent(self, agent: AspirationAgent):
        return agent.account
