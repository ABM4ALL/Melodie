# -*- coding:utf-8 -*-
import pandas as pd

from MelodieInfra import MelodieException
from Melodie import Agent, Model, Scenario
from tests.infra.config import cfg


class TestAgent(Agent):
    def setup(self):
        self.a = 123
        self.b = 456
        self.productivity = 0.0


class TestModel(Model):
    def setup(self):
        N = 10
        params_df = pd.DataFrame(
            [{"a": 123, "b": 456, "productivity": 0.0} for i in range(N)]
        )
        self.agent_list1 = self.create_agent_list(TestAgent)
        self.agent_list1.setup_agents(N, params_df)
        self.agent_list1[2].id = 1
        self.agent_list1[3].id = 1

        self.agent_list1[4].id = 5
        self.agent_list1[5].id = 5


def test_agent_container_id_check():
    tm = TestModel(config=cfg, scenario=Scenario(id_scenario=0))
    tm.setup()
    try:
        tm._check_agent_containers()
    except MelodieException as e:
        assert e.id == 1303


# what --> function
# when --> params
# then --> assert the results equal to sth
