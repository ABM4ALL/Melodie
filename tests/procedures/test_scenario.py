# -*- coding:utf-8 -*-


import os
import random
from typing import List

import pandas as pd
import pytest

from Melodie import (
    Agent,
    DataCollector,
    Environment,
    Scenario,
    Simulator,
    Model,
    DataLoader,
    Config,
)

cfg_for_temp = Config(
    "temp_db_for_parallel_simulation",
    os.path.dirname(__file__),
    input_folder=os.path.join(os.path.dirname(
        __file__), "resources", "excels"),
    output_folder=os.path.join(os.path.dirname(
        __file__), "resources", "output/test_scenario"),
)
AGENT_NUM_1 = 10
AGENT_NUM_2 = 20


class DFLoader(DataLoader):
    pass


class TestAgent(Agent):
    def setup(self):
        self.a = 123
        self.b = 456
        self.productivity = 0  # self.productivity


class TestEnv(Environment):
    def setup(self):
        pass


class TestScenario(Scenario):
    def load_data(self):
        self.demo_data1 = self.load_dataframe("demo-data.xlsx")
        self.demo_data2 = self.load_dataframe("demo-data.csv")
        self.demo_matrix1 = self.load_matrix("demo-matrix.xlsx")
        self.demo_matrix2 = self.load_matrix("demo-matrix.csv")

    def setup(self):
        self.period_num = 1
        self.productivity = random.random()

    # def setup(self):

        # self.demo_matrix1 = self.load


class DCTestModel(Model):
    scenario: TestScenario

    def setup(self):
        params_df_1 = pd.DataFrame(
            [{"id": i, "a": 1, "b": 1, "productivity": 0} for i in range(10)]
        )
        params_df_2 = pd.DataFrame(
            [{"id": i, "a": 1, "b": 1, "productivity": 0} for i in range(20)]
        )
        # params_df_3 = pd.DataFrame(
        #     [{"a": 1.0, "b": 1, "productivity": 0} for i in range(20)]
        # )
        self.agent_list1 = self.create_agent_container(
            TestAgent, 10, params_df_1)
        self.agent_list1.setup_agents(10, params_df_1)
        self.agent_list2 = self.create_agent_container(
            TestAgent, 20, params_df_2)
        self.agent_list2.setup_agents(20, params_df_2)
        self.environment = self.create_environment(TestEnv)
        # self.data_collector = self.create_data_collector(DataCollector1)

    def run(self):
        assert isinstance(self.scenario.demo_data1, pd.DataFrame)
        assert self.scenario.demo_data1.shape[0] == 5

        assert isinstance(self.scenario.demo_data2, pd.DataFrame)
        assert self.scenario.demo_data2.shape[0] == 5

        assert self.scenario.demo_matrix1.shape == (4, 4)
        assert self.scenario.demo_matrix2.shape == (4, 4)


class Simulator4Test(Simulator):
    def register_scenario_dataframe(self) -> None:
        pass

    def register_generated_dataframes(self):
        return

    def register_static_dataframes(self):
        return

    def generate_scenarios(self) -> List[TestScenario]:
        scenarios = [TestScenario(id_scenario=i) for i in range(2)]
        for s in scenarios:
            s.run_num = 2
            s.manager = self
            s.initialize()
        return scenarios


@pytest.mark.timeout(15)
def test_load_data():
    s = Simulator4Test(cfg_for_temp, TestScenario, DCTestModel)
    # s.data_loader.load_dataframe("demo-data.xlsx")
    s.run()
