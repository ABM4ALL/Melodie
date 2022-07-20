# -*- coding:utf-8 -*-
from typing import List

import pytest

from Melodie import (
    Agent,
    Model,
    Scenario,
    GATrainerParams,
    Trainer,
    DataFrameLoader,
    Environment,
)
from Melodie.algorithms.ga_trainer import GATrainerAlgorithm
from Melodie.algorithms.meta import GATrainerAlgorithmMeta
from .config import cfg


class DemoAgent(Agent):
    def setup(self):
        self.param1 = 0.0
        self.param2 = 0.0


class NewModel(Model):
    def setup(self):
        self.environment = Environment()
        self.agent_list = self.create_agent_container(DemoAgent, 10)


class DFLoader(DataFrameLoader):
    def generate_scenarios(self, manager_type: str) -> List["Scenario"]:
        return [Scenario(0)]


class MockTrainer(Trainer):
    def setup(self):
        self.add_container(
            "agent_list", ["param1", "param2"], [], lambda s: [i for i in range(10)]
        )

    def target_function(self, agent: DemoAgent) -> float:
        return agent.param1 ** 2 + agent.param2 ** 2


@pytest.mark.timeout(30)
def test_chrom_params_algorithm():
    params = GATrainerParams(
        0, 5, 50, 20, 0.02, 20, param1_min=-1, param1_max=1, param2_min=-1, param2_max=1
    )
    mgr = MockTrainer(cfg, Scenario, NewModel, DFLoader, 1)
    mgr.setup()
    mgr.pre_run()
    ta = GATrainerAlgorithm(params, mgr)
    scenario = Scenario(0)
    meta = GATrainerAlgorithmMeta()

    ta.run(scenario, meta)
