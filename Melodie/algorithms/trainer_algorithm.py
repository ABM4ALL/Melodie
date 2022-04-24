# -*- coding:utf-8 -*-
# @Time: 2022/4/8 16:22
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: trainer_algorithm.py
from typing import Dict, Tuple, Callable, Union, List, ClassVar

from sko.GA import GA

from Melodie import AgentList, Model, Agent, Config, Scenario
from ..basic import MelodieExceptions
from ..simulator import BaseModellingManager


class TargetFcnCache:
    def __init__(self):
        self.target_fcn_record: Dict[Tuple[int, int], Dict] = {}
        self.current_generation = -1
        self.current_chromosome_id = -1

    def lookup_agent_target_value(self, agent_id: int, agent_category: int, generation: int, chromosome_id: int):
        return self.target_fcn_record[(generation, chromosome_id)][(agent_id, agent_category)]

    def set_agent_target_value(self, agent_id: int, agent_category: int, value: float, generation: int,
                               chromosome_id: int):
        # self.current_target_fcn_value[(agent_id, agent_category)] = value
        if (generation, chromosome_id) not in self.target_fcn_record:
            self.target_fcn_record[(generation, chromosome_id)] = {}
        self.target_fcn_record[(generation, chromosome_id)][(agent_id, agent_category)] = value

    def best_value(self, chromosome_num: int, generation: int, agent_id: int, agent_category: int):
        values = [self.target_fcn_record[(generation, chromosome_id)][(agent_id, agent_category)] for chromosome_id in
                  range(chromosome_num)]
        return min(values)


class TrainerAlgorithm(BaseModellingManager):
    """
    参数：一个tuple
    每次会跑20条染色体，然后将参数缓存起来。
    目标函数从TargetFcnCache中查询。
    """

    def __init__(self, config: Config, scenario_cls: ClassVar[Model], model_cls: ClassVar[Model], df_loader_cls=None):
        super().__init__(config, scenario_cls, model_cls, df_loader_cls)
        self._config = config
        self._model_cls: ClassVar[Model] = model_cls
        self._scenario_cls: ClassVar[Scenario] = scenario_cls
        self.chromosomes = 20

        self.algorithms_dict: Dict[Tuple[int, int], Union[GA]] = {}
        self.target_fcn_cache = TargetFcnCache()
        self.agent_container_getters: Dict[int, Callable[[], AgentList]] = {}
        self.agent_params_defined: Dict[int, List[str]] = {}  # category: [param_name1, param_name2...]

        self._current_model: Model = None

        self._chromosome_counter = 0
        self._current_generation = 0

    def generate_scenarios(self) -> List['Scenario']:
        """
        Generate scenarios from the dataframe_loader
        :return:
        """
        scenario = self.scenario_cls(0)
        scenario.setup()
        return [scenario]
        # if self.df_loader is None:
        #     raise MelodieExceptions.Data.NoDataframeLoaderDefined()
        # return self.df_loader.generate_scenarios('trainer')

    def add_agent_container(self, container_name: str, container_id: int, param_names: List[str],
                            agent_id_list: List[int]):
        assert container_id not in self.agent_container_getters
        self.agent_container_getters[container_id] = lambda: getattr(self._current_model, container_name)
        for agent_id in agent_id_list:
            self.algorithms_dict[(agent_id, container_id)] = GA(func=self.target_function(agent_id, container_id),
                                                                n_dim=len(param_names), size_pop=self.chromosomes, max_iter=80,
                                                                prob_mut=0.02, lb=[0, 0, 0], ub=[1, 1, 1],
                                                                precision=1e-5)
        self.agent_params_defined[container_id] = param_names

    def params_from_algorithm_to_agent_container(self, chromosome_id: int):
        for key, algorithm in self.algorithms_dict.items():
            chromosome_value = algorithm.chrom2x(algorithm.Chrom)[chromosome_id]
            agent_id, agent_category = key
            container: Union[AgentList] = self.agent_container_getters[agent_category]()
            agent = container.get_agent(agent_id)
            for i, param_name in enumerate(self.agent_params_defined[agent_category]):
                setattr(agent, param_name, chromosome_value[i])

    def target_function_from_model_to_cache(self, target_fcn: Callable[[Agent], float], generation: int,
                                            chromosome_id: int, ):
        """
        将Model中的目标函数值提取出来，放到cache里面。
        :return:
        """
        for container_category, container_getter in self.agent_container_getters.items():
            container = container_getter()
            for agent in container:
                val = target_fcn(agent)
                self.target_fcn_cache.set_agent_target_value(agent.id, container_category, val, generation,
                                                             chromosome_id)

    def target_function(self, agent_id: int, agent_category: int) -> Callable:
        def f(*args):
            self._chromosome_counter += 1
            if self._chromosome_counter == self.chromosomes:
                best = self.target_fcn_cache.best_value(self.chromosomes, self._current_generation, agent_id,
                                                        agent_category)  # TODO:How to represent the best result??
                if agent_id == 0:
                    print('best', args, best, self._current_generation)
                return best
            elif self._chromosome_counter > self.chromosomes:
                raise ValueError
            else:
                value = self.target_fcn_cache.lookup_agent_target_value(agent_id, agent_category,
                                                                        self._current_generation,
                                                                        self._chromosome_counter)
                # print('value', value, (agent_id, agent_category, self._current_generation,
                #                        self._chromosome_counter))
                return value

        return f

    def target_fcn(self, agent: Agent):
        pass

    def create_model(self):
        scenario = self._scenario_cls(0)

        model = self._model_cls(self._config, scenario)
        scenario.manager = self
        model.setup()
        return model

    def run(self):
        self.pre_run()

        for i in range(50):
            self._current_generation = i
            print("=======================" * 10, i)
            print(self.algorithms_dict[(0, 0)].chrom2x(self.algorithms_dict[(0, 0)].Chrom))
            for chromosome_id in range(self.chromosomes):
                self._current_model = self.create_model()
                self.params_from_algorithm_to_agent_container(chromosome_id)
                self._current_model.run()

                self.target_function_from_model_to_cache(self.target_fcn, i, chromosome_id)

            # 运行一步
            for key, algorithm in self.algorithms_dict.items():
                self._chromosome_counter = -1
                algorithm.run(1)
            print(self.algorithms_dict[(0, 0)].best_x, self.algorithms_dict[(0, 0)].best_y)
