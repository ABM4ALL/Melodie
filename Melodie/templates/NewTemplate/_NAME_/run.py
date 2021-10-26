# -*- coding:utf-8 -*-
# @Time: {{cookiecutter.created_at}}
# @Author: {{cookiecutter.author}}
# @Email: {{cookiecutter.email}}

import os

from Melodie import OldConfig, run_new
from config import config
from model.core.agent import _ALIAS_Agent
# from model.core.analyzer import _ALIAS_Analyzer
from model.core.data_collector import _ALIAS_DataCollector
from model.core.environment import _ALIAS_Environment
from model.core.model import _ALIAS_Model
from model.core.scenario import _ALIAS_Scenario

# from model.core.scenario_manager import _ALIAS_ScenarioManager
# from model.core.table_generator import _ALIAS_TableGenerator

run_new(
    config,
    model_class=_ALIAS_Model,
    # data_collector_class=_ALIAS_DataCollector,
    # scenario_manager_class=_ALIAS_ScenarioManager,
    # table_generator_class=_ALIAS_TableGenerator,
    # analyzer_class=_ALIAS_Analyzer
)
