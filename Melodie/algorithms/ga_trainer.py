# -*- coding:utf-8 -*-
# @Time: 2022/4/8 16:22
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: trainer_algorithm.py
import time
from typing import Dict, Tuple, Callable, Union, List, ClassVar, Any
import cloudpickle
import numpy as np
import pandas as pd
from sko.GA import GA

from Melodie import AgentList, Model, Agent, Config, Scenario, GATrainerParams, Trainer, create_db_conn
from .meta import GATrainerAlgorithmMeta


class MelodieGA(GA):
    def run(self, max_iter=None):
        self.max_iter = max_iter or self.max_iter
        best = []
        for i in range(self.max_iter):
            self.X = self.chrom2x(self.Chrom)
            self.Y = self.x2y()
            self.ranking()
            self.selection()
            self.crossover()
            self.mutation()

            # record the best ones
            generation_best_index = self.FitV.argmax()
            self.generation_best_X.append(self.X[generation_best_index, :])
            self.generation_best_Y.append(self.Y[generation_best_index])
            self.all_history_Y.append(self.Y)
            self.all_history_FitV.append(self.FitV)

            if self.early_stop:
                best.append(min(self.generation_best_Y))
                if len(best) >= self.early_stop:
                    if best.count(min(best)) == len(best):
                        break
                    else:
                        best.pop(0)

        global_best_index = np.array(self.generation_best_Y).argmin()
        self.best_x = self.generation_best_X[global_best_index]
        self.best_y = self.generation_best_Y[global_best_index]
        return self.best_x, self.best_y


class TargetFcnCache:
    """
    The cache for the pre-computed values.

    Dict:  {(generation_id,
             chromosome_id):
                           {(agent_id,
                             container_name):
                                            function_value
                           }
          }
    """

    def __init__(self):
        self.target_fcn_record: Dict[Tuple[int, int], Dict] = {}
        self.current_generation = -1
        self.current_chromosome_id = -1

    def lookup_agent_target_value(self, agent_id: int, container_name: str, generation: int, chromosome_id: int):
        return self.target_fcn_record[(generation, chromosome_id)][(agent_id, container_name)]

    def set_agent_target_value(self, agent_id: int, container_name: str, value: float, generation: int,
                               chromosome_id: int):
        # self.current_target_fcn_value[(agent_id, container_name)] = value
        if (generation, chromosome_id) not in self.target_fcn_record:
            self.target_fcn_record[(generation, chromosome_id)] = {}
        self.target_fcn_record[(generation, chromosome_id)][(agent_id, container_name)] = value

    def best_value(self, chromosome_num: int, generation: int, agent_id: int, agent_category: int):
        values = [self.target_fcn_record[(generation, chromosome_id)][(agent_id, agent_category)] for chromosome_id in
                  range(chromosome_num)]
        return min(values)


class GATrainerAlgorithm:
    """
    参数：一个tuple
    每次会跑20条染色体，然后将参数缓存起来。
    目标函数从TargetFcnCache中查询。
    """

    def __init__(self, config: Config, scenario_cls: ClassVar[Model], model_cls: ClassVar[Model],
                 params: GATrainerParams, manager: Trainer = None):
        self.manager = manager
        self.params = params
        self._config = config
        self._model_cls: ClassVar[Model] = model_cls
        self._scenario_cls: ClassVar[Scenario] = scenario_cls
        self.chromosomes = 20
        self.target_fcn: Callable[[Agent], float] = None
        self.algorithms_dict: Dict[Tuple[int, str], Union[GA]] = {}

        self.target_fcn_cache = TargetFcnCache()
        self.agent_container_getters: Dict[str, Callable[[Model], AgentList]] = {}
        self.agent_ids: Dict[str, List[int]] = {}  # {category : [agent_id]}
        self.agent_params_defined: Dict[str, List[str]] = {}  # category: [param_name1, param_name2...]
        self.recorded_agent_properties: Dict[str, List[str]] = {}  # category: [prop1, prop2...]
        self.recorded_env_properties: List[str] = []  # category: [prop1, prop2...]

        self._chromosome_counter = 0
        self._current_generation = 0

    def add_agent_container(self, container_name: str,
                            param_names: List[str],
                            recorded_properties: List[str],
                            agent_id_list: List[int]):
        assert container_name not in self.agent_container_getters
        self.agent_container_getters[container_name] = lambda model: getattr(model, container_name)
        lb, ub = self.params.bounds(param_names)
        for agent_id in agent_id_list:
            self.algorithms_dict[(agent_id, container_name)] = MelodieGA(
                func=self.target_function(agent_id, container_name),
                n_dim=len(param_names),
                size_pop=self.params.strategy_population,
                max_iter=self.params.number_of_generation,
                prob_mut=self.params.mutation_prob,
                lb=lb,
                ub=ub,
                precision=1e-5)
        self.agent_params_defined[container_name] = param_names
        self.recorded_agent_properties[container_name] = recorded_properties
        self.agent_ids[container_name] = agent_id_list

    def params_from_algorithm_to_agent_container(self, model: Model, chromosome_id: int):
        """
        Pass parameters from the chromosome to the agent container.

        :param model: Melodie Model
        :param chromosome_id:
        :return:
        """
        for key, algorithm in self.algorithms_dict.items():
            chromosome_value = algorithm.chrom2x(algorithm.Chrom)[chromosome_id]
            agent_id, agent_category = key
            container: Union[AgentList] = self.agent_container_getters[agent_category](model)
            agent = container.get_agent(agent_id)
            for i, param_name in enumerate(self.agent_params_defined[agent_category]):
                setattr(agent, param_name, chromosome_value[i])

    def target_function_from_model_to_cache(self, model: Model, target_fcn: Callable[[Agent], float], generation: int,
                                            chromosome_id: int, ):
        """
        Extract the value of target functions from Model, and write them into cache.

        :return:
        """
        for container_category, container_getter in self.agent_container_getters.items():
            container = container_getter(model)
            for agent in container:
                val = target_fcn(agent)
                self.target_fcn_cache.set_agent_target_value(agent.id, container_category, val, generation,
                                                             chromosome_id)

    def target_function(self, agent_id: int, container_name: str) -> Callable[[], float]:
        def f(*args):
            self._chromosome_counter += 1
            value = self.target_fcn_cache.lookup_agent_target_value(agent_id, container_name,
                                                                    self._current_generation,
                                                                    self._chromosome_counter)
            return value

        return f

    def create_model(self, scenario: Scenario):
        model = self._model_cls(self._config, scenario)
        scenario.manager = self.manager
        model.setup()
        return model

    def record_agent_properties(self, model: Model, meta: GATrainerAlgorithmMeta):
        """
        Record the property of each agent in the current chromosome.

        :param model:
        :param meta:
        :return:
        """
        agent_records = []
        env_record = {}
        meta_dict = meta.to_dict(public_only=True)

        for container_name, agent_container_getter in self.agent_container_getters.items():
            for agent in agent_container_getter(model):
                d = {}
                d.update(meta_dict)
                d['agent_id'] = agent.id
                d["target_function_value"] = self.target_fcn(agent)
                for prop_name in self.recorded_agent_properties[container_name]:
                    d[prop_name] = getattr(agent, prop_name)

                agent_records.append(d)
        environment = model.environment
        env_record.update(meta_dict)
        env_record.update({prop_name: getattr(environment, prop_name) for prop_name in self.recorded_env_properties})
        create_db_conn(self.manager.config).write_dataframe('agent_trainer_result',
                                                            pd.DataFrame(agent_records),
                                                            if_exists="append")
        create_db_conn(self.manager.config).write_dataframe('env_trainer_result',
                                                            pd.DataFrame([env_record]),
                                                            if_exists="append")
        return agent_records, env_record

    def calc_cov_df(self, df, env_df: pd.DataFrame, meta):

        pd.set_option('max_colwidth', 500)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        meta_dict = meta.to_dict(public_only=True)
        meta_dict.pop("chromosome_id")
        for container_name in self.agent_ids.keys():
            container_agent_record_list = []
            for agent_id in self.agent_ids[container_name]:
                agent_data = df.loc[df["agent_id"] == agent_id]
                cov_records = {}
                cov_records.update(meta_dict)
                for prop_name in self.recorded_agent_properties[container_name] + ['target_function_value']:
                    p: pd.Series = agent_data[prop_name]
                    mean = p.mean()
                    cov = p.std() / p.mean()
                    cov_records.update({prop_name + '_mean': mean, prop_name + '_cov': cov})
                container_agent_record_list.append(cov_records)
            create_db_conn(self.manager.config).write_dataframe('agent_trainer_result_cov',
                                                                pd.DataFrame(container_agent_record_list),
                                                                if_exists="append")
        env_record = {}
        env_record.update(meta_dict)
        for prop_name in self.recorded_env_properties:
            mean = env_df[prop_name].mean()
            cov = env_df[prop_name].std() / env_df[prop_name].mean()
            env_record.update({prop_name + '_mean': mean, prop_name + '_cov': cov})
        create_db_conn(self.manager.config).write_dataframe('env_trainer_result_cov',
                                                            pd.DataFrame([env_record]),
                                                            if_exists="append")

    def pre_check(self, meta):
        """
        Check at the beginning of run()
        :return:
        """
        print("Algorithm will run with:")
        print("    Meta value", meta)
        print("    Recording environment parameters: ", self.recorded_env_properties)
        print("    Recording Agent containers:", self.agent_container_getters)

    def run(self, scenario: Scenario, meta: Union[GATrainerAlgorithmMeta]):
        self.pre_check(meta)

        for i in range(self.params.number_of_generation):
            self._current_generation = i
            meta.iteration = i
            print(f"======================="
                  f"Path {meta.path_id} Iteration {i + 1}/{self.params.number_of_generation}"
                  f"=======================")
            agent_records_collector: List[List[Dict[str, Any]]] = []
            env_records_list: List[Dict[str, Any]] = []
            for chromosome_id in range(self.chromosomes):
                meta.chromosome_id = chromosome_id
                _current_model = self.create_model(scenario)
                self.params_from_algorithm_to_agent_container(_current_model, chromosome_id)
                t0 = time.time()
                cloudpickle.dumps(_current_model)
                t1 = time.time()
                print(t1 - t0)
                _current_model.run()
                agent_records, env_record = self.record_agent_properties(_current_model, meta)
                agent_records_collector += agent_records
                env_records_list.append(env_record)

                self.target_function_from_model_to_cache(_current_model, self.target_fcn, i, chromosome_id)

            self.calc_cov_df(pd.DataFrame(agent_records_collector),
                             pd.DataFrame(env_records_list), meta)

            for key, algorithm in self.algorithms_dict.items():
                self._chromosome_counter = -1
                algorithm.run(1)
