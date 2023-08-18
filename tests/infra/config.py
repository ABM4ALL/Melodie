# -*- coding:utf-8 -*-
import os
import sys

from Melodie import Config, Model, Scenario

skip_env_dependent = "--skip-env-dependent-testcases" in sys.argv
resources_path = os.path.join(os.path.dirname(__file__), "resources")

cfg = Config(
    "test",
    os.path.dirname(__file__),
    input_folder=os.path.join(os.path.dirname(__file__), "resources", "excels"),
    output_folder=os.path.join(os.path.dirname(__file__), "resources", "output"),
)

cfg_for_temp = Config(
    "temp_db_created",
    os.path.dirname(__file__),
    input_folder=os.path.join(os.path.dirname(__file__), "resources", "excels"),
    output_folder=os.path.join(os.path.dirname(__file__), "resources", "output"),
)
cfg_for_calibrator = Config(
    "temp_db_calibrator",
    os.path.dirname(__file__),
    input_folder=os.path.join(os.path.dirname(__file__), "resources", "excels"),
    output_folder=os.path.join(os.path.dirname(__file__), "resources", "output"),
)
cfg_for_trainer = Config(
    "temp_db_trainer",
    os.path.dirname(__file__),
    input_folder=os.path.join(os.path.dirname(__file__), "resources", "excels"),
    output_folder=os.path.join(os.path.dirname(__file__), "resources", "output"),
)

cfg_dataloader_with_cache = Config(
    "loader_with_cache",
    os.path.dirname(__file__),
    input_folder=os.path.join(os.path.dirname(__file__), "resources", "excels"),
    output_folder=os.path.join(os.path.dirname(__file__), "resources", "output"),
    input_dataframe_cache=True,
)
cfg_dataloader_without_cache = Config(
    "loader_without_cache",
    os.path.dirname(__file__),
    input_folder=os.path.join(os.path.dirname(__file__), "resources", "excels"),
    output_folder=os.path.join(os.path.dirname(__file__), "resources", "output"),
)

model = Model(
    cfg,
    Scenario(id_scenario=100),
)
