# -*- coding:utf-8 -*-
# import pytest
import os
from typing import List

from Melodie import Agent, Config, DataLoader, Environment, Model, Scenario, Trainer

cfg_for_trainer = Config(
    "temp_db_trainer",
    os.path.dirname(__file__),
    input_folder=os.path.join(os.path.dirname(__file__), "resources", "excels"),
    output_folder=os.path.join(
        os.path.dirname(__file__), "resources", "output", "trainer"
    ),
)


class DemoAgent(Agent):
    def setup(self):
        self.param1 = 0.0
        self.param2 = 0.0


class NewModel(Model):
    def setup(self):
        self.environment = Environment()
        self.agent_list = self.create_agent_container(DemoAgent, 10)
        self.agent_list.setup_agents(10)


class DFLoader(DataLoader):
    def generate_scenarios(self, manager_type: str) -> List["Scenario"]:
        return [Scenario(0)]


class MockTrainer(Trainer):
    def setup(self):
        self.add_agent_training_property(
            "agent_list", ["param1", "param2"], lambda s: [i for i in range(10)]
        )

    def utility(self, agent: Agent) -> float:
        return -(agent.param1**2 + agent.param2**2)
