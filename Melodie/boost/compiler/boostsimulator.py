# # -*- coding:utf-8 -*-
# # @Time: 2021/10/21 17:16
# # @Author: Zhanyi Hou
# # @Email: 1295752786@qq.com
# # @File: BoostSimulator.py
# import importlib
# import sys
# import time
# import logging
#
# from Melodie.visualization import Visualizer
#
# logging.basicConfig(stream=sys.stderr, level=logging.INFO)
# logger = logging.getLogger(__name__)
#
# from typing import ClassVar, List
#
# import pandas as pd
#
# from Melodie import Simulator, Config, Scenario, Model
# from Melodie.boost.compiler.compiler import conv
#
#
# class BoostSimulator(Simulator):
#     def create_scenarios_dataframe(self) -> pd.DataFrame:
#         return pd.DataFrame([{"id": i, "win_prob": 0.4} for i in range(100)])
#
#     def generate_scenarios(self) -> List['Scenario']:
#         pass
#
#     def run_boost(self,
#                   agent_class: ClassVar['Agent'],
#                   environment_class: ClassVar['Environment'],
#                   config: 'Config' = None,
#                   data_collector_class: ClassVar['DataCollector'] = None,
#                   model_class: ClassVar['Model'] = None,
#                   scenario_class: ClassVar['Scenario'] = None,
#                   scenario_manager_class: ClassVar['ScenarioManager'] = None,
#                   table_generator_class: ClassVar['TableGenerator'] = None,
#                   analyzer_class: ClassVar['Analyzer'] = None,
#                   visualizer_class: ClassVar['Visualizer'] = None,
#                   boost_model_class: ClassVar['Model'] = None,
#                   model_components=None
#                   ):
#         conv(agent_class, environment_class, model_class, 'out.py', model_components=model_components)
#         logger.warning("Testing. compilation finished, program exits")
#         # return
#         compiled = importlib.import_module('out')
#         model_run = compiled.__getattribute__('___model___run')
#         logger.info("Preprocess compilation finished, now running pre-run procedures.")
#
#         self.config = config
#         self.scenario_class = scenario_class
#         self.register_scenario_dataframe()
#         self.register_static_dataframes()
#
#         # self.scenarios_dataframe = self.create_scenarios_dataframe()
#         self.scenarios = self.generate_scenarios()
#         assert self.scenarios is not None
#         logger.info("Pre-run procedures finished. Now simulation starts...")
#
#         t0 = time.time()
#         t1 = time.time()
#         first_run_finished_at = time.time()
#         first_run = True
#         for scenario in self.scenarios:
#             for run_id in range(scenario.number_of_run):
#                 if first_run:
#                     logger.info("Numba is now taking control of program. "
#                                 "It may take a few seconds for compilation.")
#                 visualizer = visualizer_class()
#                 visualizer.setup()
#                 visualizer.current_scenario = scenario
#                 model = boost_model_class(self.config,
#                                           scenario,
#                                           visualizer=visualizer
#                                           )
#                 model.setup_boost()
#                 model_run(model)
#                 if first_run:
#                     logger.info("The first run has completed, and numba has finished compilaiton. "
#                                 "Your program will be speeded up greatly.")
#                     first_run_finished_at = time.time()
#                     first_run = False
#
#                 logger.info(f"Finished running <experiment {run_id}, scenario {scenario.id}>. "
#                             f"time elapsed: {time.time() - t1}s")
#                 t1 = time.time()
#
#         logger.info(f"totally time elapsed {time.time() - t0} s,"
#                     f" {(time.time() - t0) / 100}s per run, {(time.time() - first_run_finished_at) / (100 - 1)}s per run after compilation")
