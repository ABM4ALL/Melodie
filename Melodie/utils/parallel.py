import base64
import importlib
import json
import multiprocessing
import queue
import sys
import time
from typing import Dict, Tuple, Any

import cloudpickle

from Melodie.global_configs import MelodieGlobalConfig
from Melodie.utils.system_info import is_windows

params_queue = multiprocessing.Queue() if not is_windows() else queue.Queue()
result_queue = multiprocessing.Queue() if not is_windows() else queue.Queue()


# def sub_routine_calibrator(
#     proc_id: int, modules: Dict[str, Tuple[str, str]], config_raw: Dict[str, Any]
# ):
#     """
#     The sub iterator callback for parallelized computing used in Trainer and Calibrator.
#
#     :param proc_id:
#     :param modules:
#     :param config_raw:
#     :return:
#     """
#     from Melodie import Config, Environment, Calibrator
#
#     try:
#         config = Config.from_dict(config_raw)
#         import logging
#
#         logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
#         logger = logging.getLogger(f"Calibrator-processor-{proc_id}")
#         logger.info("subroutine started!")
#
#         classes_dict = {}
#         for module_type, content in modules.items():
#             class_name, module_name = content
#             module = importlib.import_module(module_name)
#             cls = getattr(module, class_name)
#             classes_dict[module_type] = cls
#
#         calibrator: Calibrator = classes_dict["trainer"](
#             config=config,
#             scenario_cls=classes_dict["scenario"],
#             model_cls=classes_dict["model"],
#             data_loader_cls=classes_dict["data_loader"],
#         )
#         calibrator.setup()
#         calibrator.collect_data()
#         calibrator.subworker_prerun()
#     except BaseException:
#         import traceback
#
#         traceback.print_exc()
#         return
#     while 1:
#         try:
#             ret = params_queue.get()
#             t0 = time.time()
#
#             chrom, d, env_params = json.loads(ret)
#             logger.debug(f"processor {proc_id} got chrom {chrom}")
#             scenario = classes_dict["scenario"]()
#             scenario.manager = calibrator
#             scenario.setup()
#             scenario.set_params(d)
#             scenario.set_params(env_params)
#             model = classes_dict["model"](config, scenario)
#             model.create()
#             model._setup()
#             model.run()
#             agent_data = {}
#             for container_name, props in calibrator.recorded_agent_properties.items():
#                 agent_container = getattr(model, container_name)
#                 df = agent_container.to_list(props)
#                 agent_data[container_name] = df
#                 for row in df:
#                     row["agent_id"] = row.pop("id")
#             env: Environment = model.environment
#             env_data = env.to_dict(
#                 calibrator.properties + calibrator.watched_env_properties
#             )
#             env_data["target_function_value"] = calibrator.target_function(env)
#             env_data["distance"] = calibrator.distance(env)
#             # env_data["utility"] = trainer.utility(env)
#             dumped = cloudpickle.dumps((chrom, agent_data, env_data))
#             t1 = time.time()
#             logger.info(
#                 f"Processor {proc_id}, chromosome {chrom}, time: {MelodieGlobalConfig.Logger.round_elapsed_time(t1 - t0)}s"
#             )
#             result_queue.put(base64.b64encode(dumped))
#         except Exception:
#             import traceback
#
#             traceback.print_exc()
#
#
# def sub_routine_trainer(
#     proc_id: int, modules: Dict[str, Tuple[str, str]], config_raw: Dict[str, Any]
# ):
#     """
#     The sub iterator callback for parallelized computing used in Trainer and Calibrator.
#
#     :param proc_id:
#     :param modules:
#     :param config_raw:
#     :return:
#     """
#     from Melodie import Config, Trainer, Environment, AgentList, Agent
#
#     try:
#         config = Config.from_dict(config_raw)
#         import logging
#
#         logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
#         logger = logging.getLogger(f"Trainer-processor-{proc_id}")
#         logger.info("subroutine started!")
#
#         classes_dict = {}
#         for module_type, content in modules.items():
#             class_name, module_name = content
#             module = importlib.import_module(module_name)
#             cls = getattr(module, class_name)
#             classes_dict[module_type] = cls
#
#         trainer: Trainer = classes_dict["trainer"](
#             config=config,
#             scenario_cls=classes_dict["scenario"],
#             model_cls=classes_dict["model"],
#             data_loader_cls=classes_dict["data_loader"],
#         )
#         trainer.setup()
#         trainer.collect_data()
#         trainer.subworker_prerun()
#     except BaseException:
#         import traceback
#
#         traceback.print_exc()
#         return
#     while 1:
#         try:
#             ret = params_queue.get()
#             t0 = time.time()
#
#             chrom, d, agent_params = json.loads(ret)
#             logger.debug(f"processor {proc_id} got chrom {chrom}")
#             scenario = classes_dict["scenario"]()
#             scenario.setup()
#             scenario.set_params(d)
#             model = classes_dict["model"](config, scenario)
#             scenario.manager = trainer
#             model.create()
#             model._setup()
#             # {category: [{id: 0, param1: 1, param2: 2, ...}]}
#             for category, params in agent_params.items():
#                 agent_container: AgentList[Agent] = getattr(model, category)
#                 for param in params:
#                     agent = agent_container.get_agent(param["id"])
#                     agent.set_params(param)
#             model.run()
#             agent_data = {}
#             for container in trainer.container_manager.agent_containers:
#                 agent_container = getattr(model, container.container_name)
#                 df = agent_container.to_list(container.recorded_properties)
#                 agent_data[container.container_name] = df
#                 for row in df:
#                     agent = agent_container.get_agent(row["id"])
#                     row["target_function_value"] = trainer.target_function(agent)
#                     row["utility"] = trainer.utility(agent)
#                     row["agent_id"] = row.pop("id")
#             env: Environment = model.environment
#             env_data = env.to_dict(trainer.environment_properties)
#             dumped = cloudpickle.dumps((chrom, agent_data, env_data))
#             t1 = time.time()
#             logger.info(
#                 f"Processor {proc_id}, chromosome {chrom}, time: {MelodieGlobalConfig.Logger.round_elapsed_time(t1 - t0)}s"
#             )
#             result_queue.put(base64.b64encode(dumped))
#         except Exception:
#             import traceback
#
#             traceback.print_exc()
