# -*- coding:utf-8 -*-


import os
import random
from typing import List

import pandas as pd

from Melodie import (
    Agent,
    Config,
    DataCollector,
    DataLoader,
    Environment,
    Model,
    Scenario,
    Simulator,
)

cfg_for_temp = Config(
    "temp_db_created",
    os.path.dirname(__file__),
    input_folder=os.path.join(os.path.dirname(__file__), "resources", "excels"),
    output_folder=os.path.join(os.path.dirname(__file__), "resources", "output"),
    data_output_type="sqlite",
)
cfg_for_calibrator = Config(
    "temp_db_calibrator",
    os.path.dirname(__file__),
    input_folder=os.path.join(os.path.dirname(__file__), "resources", "excels"),
    output_folder=os.path.join(os.path.dirname(__file__), "resources", "output"),
    data_output_type="sqlite",
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
    def setup(self):
        self.period_num = 1
        self.productivity = random.random()


class DCTestModel(Model):
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
        self.agent_list1 = self.create_agent_container(TestAgent, 10, params_df_1)
        self.agent_list1.setup_agents(10, params_df_1)
        self.agent_list2 = self.create_agent_container(TestAgent, 20, params_df_2)
        self.agent_list2.setup_agents(20, params_df_2)
        self.environment = self.create_environment(TestEnv)
        self.data_collector = self.create_data_collector(DataCollector1)


class Simulator4Test(Simulator):
    def register_scenario_dataframe(self) -> None:
        pass

    def register_generated_dataframes(self):
        return

    def register_static_dataframes(self):
        return

    def generate_scenarios(self) -> List["Scenario"]:
        scenarios = [TestScenario() for i in range(1)]
        for s in scenarios:
            s.manager = self
        return scenarios


data_collector = None


class DataCollector1(DataCollector):
    def setup(self):
        global data_collector
        data_collector = self
        self.add_agent_property("agent_list1", "a")
        self.add_agent_property("agent_list2", "b")


def test_model_run():
    global data_collector
    sim = Simulator4Test(
        config=cfg_for_temp,
        model_cls=DCTestModel,
        scenario_cls=TestScenario,
    )
    sim.run()

    dc: DataCollector = data_collector
    assert dc.status == True
    dc.collect(0)
    assert len(dc.agent_properties_dict["agent_list1"]) == AGENT_NUM_1
    assert len(dc.agent_properties_dict["agent_list2"]) == AGENT_NUM_2
    dc.collect(1)
    assert len(dc.agent_properties_dict["agent_list1"]) == AGENT_NUM_1 * 2
    assert len(dc.agent_properties_dict["agent_list2"]) == AGENT_NUM_2 * 2
    dc.save()


def test_status():
    from tests.procedures.calibrator import CovidCalibrator, CovidModel, CovidScenario

    calibrator = CovidCalibrator(
        cfg_for_calibrator, CovidScenario, CovidModel, DFLoader
    )
    scenario = calibrator.scenario_cls(0)
    scenario._setup()
    model: CovidModel = calibrator.model_cls(cfg_for_calibrator, scenario)
    model.setup()
    assert model.data_collector.status == False
