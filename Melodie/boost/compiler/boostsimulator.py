# -*- coding:utf-8 -*-
# @Time: 2021/10/21 17:16
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: BoostSimulator.py
import importlib
import time
from typing import List, ClassVar

import numpy as np
import pandas as pd

from Melodie import Simulator, NewConfig, Scenario
from Melodie.boost.compiler.compiler import conv
from Melodie.boost.compiler.src.ast_demo import GINIAgent, GiniEnvironment, GiniModel, GiniScenario


class BoostModel:
    def __init__(self, scenario):
        self.environment = np.array([(100, 0.6, 0, 0)],
                                    dtype=[('trade_num', 'i4'),
                                           ('win_prob', 'f4'),
                                           ('total_wealth', 'i4'),
                                           ('gini', 'f4')])[0]

        self.agent_manager = np.array([(i, 0, 0.5) for i in range(100)],
                                      dtype=[('id', 'i4'),
                                             ('account', 'f4'),
                                             ('productivity', 'f4'),
                                             ])

        self.scenario: Scenario = scenario
        # self.scenario.periods = 200


class BoostSimulator(Simulator):
    def create_scenarios_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame([{"win_prob": 0.4} for i in range(10)])

    def run_boost(self,
                  agent_class: ClassVar['Agent'],
                  environment_class: ClassVar['Environment'],
                  config: 'Config' = None,
                  data_collector_class: ClassVar['DataCollector'] = None,
                  model_class: ClassVar['Model'] = None,
                  scenario_class: ClassVar['Scenario'] = None,
                  scenario_manager_class: ClassVar['ScenarioManager'] = None,
                  table_generator_class: ClassVar['TableGenerator'] = None,
                  analyzer_class: ClassVar['Analyzer'] = None):
        # conv('src/ast_demo.py', 'out.py')

        self.config = config
        self.scenario_class = scenario_class
        self.register_static_tables()
        self.scenarios_dataframe = self.create_scenarios_dataframe()
        self.scenarios = self.generate_scenarios()
        assert self.scenarios is not None

        compiled = importlib.import_module('out')
        # print(dir(compiled))
        model_run = compiled.__getattribute__('___model___run')
        # self.agent_params_dataframe = self.generate_agent_params_dataframe()
        # for scenario in self.scenarios:
        # scenario = self.scenarios[0]
        t0 = time.time()
        t1 = time.time()
        for scenario in self.scenarios:
            model = BoostModel(scenario)
            model_run(model)
            print(f"run %d, time elapsed: {time.time() - t1}s")
            t1 = time.time()
        print(f"totally time elapsed {time.time()-t0} s,"
              f" {(time.time()-t0)/100}s per run")

if __name__ == "__main__":
    bs = BoostSimulator()
    bs.run_boost(GINIAgent, GiniEnvironment,
                 None, None, GiniModel, scenario_class=GiniScenario)
