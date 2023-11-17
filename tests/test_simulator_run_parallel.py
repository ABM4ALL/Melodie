# -*- coding:utf-8 -*-


import os
from MelodieInfra.config.config import Config
from tests.simulator_demo import Simulator4Test, DCTestModel, TestScenario

cfg_for_temp = Config(
    "temp_db_for_parallel_simulation",
    os.path.dirname(__file__),
    input_folder=os.path.join(os.path.dirname(__file__), "resources", "excels"),
    output_folder=os.path.join(os.path.dirname(__file__), "resources", "output"),
)
AGENT_NUM_1 = 10
AGENT_NUM_2 = 20


def test_sim_parallel():
    global data_collector
    sim = Simulator4Test(
        config=cfg_for_temp,
        model_cls=DCTestModel,
        scenario_cls=TestScenario,
    )
    sim.new_parallel(1)


test_sim_parallel()
