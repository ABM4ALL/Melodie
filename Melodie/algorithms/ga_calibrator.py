# # -*- coding:utf-8 -*-
# # @Time: 2022/4/8 16:22
# # @Author: Zhanyi Hou
# # @Email: 1295752786@qq.com
# # @File: trainer_algorithm.py
# import base64
# import importlib
# import json
# import logging
# import multiprocessing
# import sys
# import time
# from typing import Dict, Tuple, Callable, Union, List, Any, Optional, TYPE_CHECKING
# import cloudpickle
# import pandas as pd
#
# from Melodie import Scenario, GATrainerParams, create_db_conn
# from .meta import GACalibratorAlgorithmMeta
# from Melodie.basic.parallel import params_queue, result_queue, sub_routine_calibrator
#
# if TYPE_CHECKING:
#     from Melodie import Environment, Calibrator
#
# from .ga import MelodieGA, GACalibratorParams
#
#
# class GACalibratorAlgorithm:
#     """
#     参数：一个tuple
#     每次会跑20条染色体，然后将参数缓存起来。
#     目标函数从TargetFcnCache中查询。
#     """
#
#     def __init__(
#             self,
#             env_param_names: List[str],
#             recorded_env_properties: List[str],
#             recorded_agent_properties: Dict[str, List[str]],
#             params: GACalibratorParams,
#             target_func: "Callable[[Environment], Union[float, int]]",
#             manager: "Calibrator" = None,
#             processors=1,
#     ):
#         global pool
#         self.manager = manager
#         self.params = params
#         self.chromosomes = 20
#         self.target_func = target_func
#         self.env_param_names = env_param_names
#         self.recorded_env_properties = recorded_env_properties
#         self.recorded_agent_properties = recorded_agent_properties
#         lb, ub = self.params.bounds(self.env_param_names)
#         self.algorithm: Optional[MelodieGA] = MelodieGA(
#             self.generate_target_function(),
#             len(self.env_param_names),
#             self.params.strategy_population,
#             self.params.number_of_generation,
#             self.params.mutation_prob,
#             lb,
#             ub,
#             precision=1e-5,
#         )
#         self.cache: Dict[Tuple[int, int], float] = {}
#         # self.agent_container_getters: Dict[str, Callable[[Model], AgentList]] = {}
#         # self.agent_ids: Dict[str, List[int]] = {}  # {category : [agent_id]}
#         # self.agent_params_defined: Dict[str, List[str]] = {}  # category: [param_name1, param_name2...]
#         # self.recorded_agent_properties: Dict[str, List[str]] = {}  # category: [prop1, prop2...]
#         # self.recorded_env_properties: List[str] = []  # category: [prop1, prop2...]
#
#         self._chromosome_counter = 0
#         self._current_generation = 0
#         self.processors = processors
#         if pool is None:
#             pool = multiprocessing.Pool(processes=processors)
#         for i in range(processors):
#             d = {
#                 "model": (
#                     self.manager.model_cls.__name__,
#                     self.manager.model_cls.__module__,
#                 ),
#                 "scenario": (
#                     self.manager.scenario_cls.__name__,
#                     self.manager.scenario_cls.__module__,
#                 ),
#                 "trainer": (
#                     self.manager.__class__.__name__,
#                     self.manager.__class__.__module__,
#                 ),
#                 "df_loader": (
#                     self.manager.df_loader_cls.__name__,
#                     self.manager.df_loader_cls.__module__,
#                 ),
#             }
#             pool.apply_async(
#                 sub_routine_calibrator, [i, d, self.manager.config.to_dict()]
#             )
#
#     def get_params(self, chromosome_id: int) -> Dict[str, Any]:
#         """
#         Pass parameters from the chromosome to the Environment.
#
#         :param chromosome_id:
#         :return:
#         """
#         chromosome_value = self.algorithm.chrom2x(self.algorithm.Chrom)[chromosome_id]
#         env_parameters_dict = {}
#         for i, param_name in enumerate(self.env_param_names):
#             env_parameters_dict[param_name] = chromosome_value[i]
#         return env_parameters_dict
#
#     def target_function_to_cache(
#             self,
#             env_data,
#             generation: int,
#             chromosome_id: int,
#     ):
#         """
#         Extract the value of target functions from Model, and write them into cache.
#
#         :return:
#         """
#         self.cache[(generation, chromosome_id)] = env_data["target_function_value"]
#
#     def generate_target_function(self) -> Callable[[], float]:
#         """
#         Generate the target function.
#
#         :return:
#         """
#
#         def f(*args):
#             self._chromosome_counter += 1
#             value = self.cache[(self._current_generation, self._chromosome_counter)]
#             return value
#
#         return f
#
#     def record_agent_properties(
#             self,
#             agent_data: Dict[str, List[Dict[str, Any]]],
#             env_data: Dict[str, Any],
#             meta: GACalibratorAlgorithmMeta,
#     ):
#         """
#         Record the property of each agent in the current chromosome.
#
#         :param agent_data: {<agent_container_name>: [{id: 0, prop1: xxx, prop2: xxx, ...}]}
#         :param env_data: {env_prop1: xxx, env_prop2: yyy, ...}
#         :param meta:
#         :return:
#         """
#         agent_records = {}
#         env_record = {}
#         meta_dict = meta.to_dict(public_only=True)
#
#         for container_name, _ in self.recorded_agent_properties.items():
#             agent_records[container_name] = []
#             data = agent_data[container_name]
#             for agent_container_data in data:
#                 d = {}
#                 d.update(meta_dict)
#                 d.update(agent_container_data)
#
#                 agent_records[container_name].append(d)
#             create_db_conn(self.manager.config).write_dataframe(
#                 f"{container_name}_trainer_result",
#                 pd.DataFrame(agent_records[container_name]),
#                 if_exists="append",
#             )
#         env_record.update(meta_dict)
#         env_record.update(env_data)
#
#         create_db_conn(self.manager.config).write_dataframe(
#             "env_trainer_result", pd.DataFrame([env_record]), if_exists="append"
#         )
#         return agent_records, env_record
#
#     def calc_cov_df(
#             self,
#             agent_container_df_dict: Dict[str, pd.DataFrame],
#             env_df: pd.DataFrame,
#             meta,
#     ):
#         """
#         Calculate the coefficient of variation
#         :param agent_container_df_dict:
#         :param env_df:
#         :param meta:
#         :return:
#         """
#
#         pd.set_option("max_colwidth", 500)
#         pd.set_option("display.max_columns", None)
#         pd.set_option("display.max_rows", None)
#         meta_dict = meta.to_dict(public_only=True)
#         meta_dict.pop("chromosome_id")
#         for container_name in self.recorded_agent_properties.keys():
#             df = agent_container_df_dict[container_name]
#             container_agent_record_list = []
#             for agent_id in self.recorded_agent_properties[container_name]:
#                 agent_data = df.loc[df["agent_id"] == agent_id]
#                 cov_records = {}
#                 cov_records.update(meta_dict)
#                 cov_records["agent_id"] = agent_id
#                 for prop_name in self.recorded_agent_properties[container_name] + [
#                     "target_function_value"
#                 ]:
#                     p: pd.Series = agent_data[prop_name]
#                     mean = p.mean()
#                     cov = p.std() / p.mean()
#                     cov_records.update(
#                         {prop_name + "_mean": mean, prop_name + "_cov": cov}
#                     )
#                 container_agent_record_list.append(cov_records)
#             create_db_conn(self.manager.config).write_dataframe(
#                 f"{container_name}_trainer_result_cov",
#                 pd.DataFrame(container_agent_record_list),
#                 if_exists="append",
#             )
#         env_record = {}
#         env_record.update(meta_dict)
#         for prop_name in self.recorded_env_properties:
#             mean = env_df[prop_name].mean()
#             cov = env_df[prop_name].std() / env_df[prop_name].mean()
#             env_record.update({prop_name + "_mean": mean, prop_name + "_cov": cov})
#         create_db_conn(self.manager.config).write_dataframe(
#             "env_trainer_result_cov", pd.DataFrame([env_record]), if_exists="append"
#         )
#
#     def pre_check(self, meta):
#         """
#         Check at the beginning of run()
#         :return:
#         """
#         print("Algorithm will run with:")
#         print("    Meta value", meta)
#         print("    Recording environment parameters: ", self.recorded_env_properties)
#         print("    Recording Agent containers:", self.recorded_agent_properties)
#
#     def run(self, scenario: Scenario, meta: Union[GACalibratorAlgorithmMeta]):
#         self.pre_check(meta)
#
#         for i in range(self.params.number_of_generation):
#             t0 = time.time()
#             self._current_generation = i
#             meta.iteration = i
#             print(
#                 f"======================="
#                 f"Path {meta.path_id} Iteration {i + 1}/{self.params.number_of_generation}"
#                 f"======================="
#             )
#
#             for chromosome_id in range(self.params.strategy_population):
#                 params = self.get_params(chromosome_id)
#                 params_queue.put(
#                     json.dumps((chromosome_id, scenario.to_json(), params))
#                 )
#
#             agent_records_collector: Dict[str, List[Dict[str, Any]]] = {
#                 container_name: []
#                 for container_name in self.recorded_agent_properties.keys()
#             }
#             env_records_list: List[Dict[str, Any]] = []
#
#             for _chromosome_id in range(self.params.strategy_population):
#                 v = result_queue.get()
#
#                 chrom, agents_data, env_data = cloudpickle.loads(base64.b64decode(v))
#                 meta.chromosome_id = chrom
#                 agent_records, env_record = self.record_agent_properties(
#                     agents_data, env_data, meta
#                 )
#                 for container_name, records in agent_records.items():
#                     agent_records_collector[container_name] += records
#                 env_records_list.append(env_record)
#                 self.target_function_to_cache(env_data, i, chrom)
#
#             self.calc_cov_df(
#                 {k: pd.DataFrame(v) for k, v in agent_records_collector.items()},
#                 pd.DataFrame(env_records_list),
#                 meta,
#             )
#
#             self._chromosome_counter = -1
#             self.algorithm.run(1)
#             t1 = time.time()
#             print("=" * 20, "Time Elapsed", t1 - t0, "=" * 20)
#
#
# pool = None
