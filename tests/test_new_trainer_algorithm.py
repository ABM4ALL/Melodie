# -*- coding:utf-8 -*-
from typing import List

import pytest

from Melodie import (
    Agent,
    Model,
    Scenario,
    Trainer,
    DataLoader,
    Environment,
)
from Melodie.trainer import GATrainerAlgorithm, GATrainerAlgorithmMeta, GATrainerParams
from .config import cfg_for_trainer


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


@pytest.mark.timeout(30)
def test_chrom_params_algorithm():
    params = GATrainerParams(
        0, 5, 20, 20, 0.02, 20, param1_min=-1, param1_max=1, param2_min=-1, param2_max=1
    )
    mgr = MockTrainer(cfg_for_trainer, Scenario, NewModel, DFLoader, 4)
    mgr.setup()
    mgr.pre_run()
    ta = GATrainerAlgorithm(params, mgr)
    scenario = Scenario(0)
    meta = GATrainerAlgorithmMeta()
    mgr.pre_run()
    ta.run(scenario, meta)
