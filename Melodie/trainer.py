import abc
import math
import time
from typing import Type, Callable, List, Optional, ClassVar, Iterator, Union, Tuple
from abc import ABC
import copy
import numpy as np
import pandas as pd

from Melodie import Model, Scenario, Simulator, Config, Agent, create_db_conn, GALearningScenario
from Melodie.algorithms import ga

"""
training strategy interface
"""


class TrainingAlgorithm(ABC):
    def setup(self):
        pass

    def set_parameters(self, parameters_num: int):
        pass

    def set_parameters_agents(self, agent_num: int, agent_params: int):
        pass

    def optimize(self, fitness: Callable):
        pass

    def optimize_multi_agents(self, fitness, scenario):
        pass


class GeneticAlgorithm(TrainingAlgorithm):
    def __init__(self,
                 training_generations: int,
                 strategy_population_size: int,
                 mutation_prob: float,
                 strategy_param_code_length: int, ):
        self.training_generations: int = training_generations
        self.strategy_population_size = strategy_population_size
        self.mutation_prob = mutation_prob  # 突变为了避免收敛到局部最优，但太大的导致搜索不稳定
        self.strategy_param_code_length = strategy_param_code_length  # 这个值越大解的精度越高 --> 把下面区间[strategy_param_min, strategy_param_max]分得越细

        self.agent_num = 0
        self.params_each_agent = 0
        self.parameters_num = 0
        self.parameters = []
        self.parameters_value: Optional[np.ndarray] = None
        self.parameter_names = []
        self.env_property_names = []

    def set_parameters_agents(self, agent_num: int, agent_params: int, parameter_names: List[str],
                              env_property_names: List[str]):
        """

        :param agent_num:
        :param agent_params:
        :param parameter_names:
        :param env_property_names:
        :return:
        """
        self.params_each_agent = agent_params
        self.agent_num = agent_num
        self.parameters_num = self.agent_num * self.params_each_agent  # 参数的数量
        self.parameters = [(-5, 5) for i in range(self.parameters_num)]
        self.parameters_value = np.array([1 for i in range(self.parameters_num)], dtype=np.float64)
        self.parameter_names = parameter_names
        self.env_property_names = env_property_names

    def agent_params_convertion(self):
        pass

    def optimize(self, fitness: Callable):
        strategy_population = np.random.randint(2,
                                                size=(self.strategy_population_size,
                                                      self.strategy_param_code_length * self.parameters_num))
        for gen in range(0, self.training_generations):
            strategy_fitness = []
            parameter_sums = [0 for i in range(len(self.parameters))]
            parameter_values: List[List[int]] = []
            for i, strategy in enumerate(strategy_population):
                inner_parameters: List[int] = []
                for param_index in range(self.parameters_num):
                    self.parameters_value[param_index] = ga.translate_binary2real(
                        strategy[
                        param_index * self.strategy_param_code_length:
                        (param_index + 1) * self.strategy_param_code_length],
                        self.parameters[param_index][0],
                        self.parameters[param_index][1])
                    parameter_sums[param_index] += self.parameters_value[param_index]
                    inner_parameters.append(self.parameters_value[param_index])
                parameter_values.append(inner_parameters)

                strategy_fitness.append(fitness(self.parameters_value, i, meta={"chromosome_id": i}))
                assert np.isfinite(strategy_fitness).all(), f"Fitness contains infinite value {strategy_fitness}"

            ret = yield strategy_population, parameter_values, strategy_fitness
            if ret is None:
                strategy_population = ga.population_update(strategy_population, strategy_fitness,
                                                           self.mutation_prob, self.strategy_population_size)
            else:
                assert ret.shape == strategy_population.shape
                strategy_population = ret

    def optimize_multi_agents(self, fitness: Callable, scenario: Type[Scenario]):
        """
        Optimization for multi-agent system.
        :param fitness:
        :param scenario:
        :return:
        """
        strategy_population = np.random.randint(2,
                                                size=(self.strategy_population_size,
                                                      self.strategy_param_code_length * self.parameters_num))
        for gen in range(0, self.training_generations):
            strategy_fitness = []
            parameter_sums = [0 for i in range(len(self.parameters))]
            params: List[List[int]] = []
            agent_parameters = [
                [[0.0 for j in range(self.strategy_population_size)] for k in range(self.params_each_agent)] for i in
                range(self.agent_num)]
            env_parameters = {env_parameter_name: [0 for chromosome_id in strategy_population] for env_parameter_name in
                              self.env_property_names}
            for chromosome_id, strategy in enumerate(strategy_population):
                inner_parameters: List[int] = []
                for param_index in range(self.parameters_num):
                    self.parameters_value[param_index] = ga.translate_binary2real(
                        strategy[
                        param_index * self.strategy_param_code_length:
                        (param_index + 1) * self.strategy_param_code_length],
                        self.parameters[param_index][0],
                        self.parameters[param_index][1])
                    parameter_sums[param_index] += self.parameters_value[param_index]
                    inner_parameters.append(self.parameters_value[param_index])
                    agent_index = math.floor(param_index / self.params_each_agent)
                    param_index_in_agent_params = param_index % self.params_each_agent

                    agent_parameters[agent_index][param_index_in_agent_params][chromosome_id] = self.parameters_value[
                        param_index]

                params.append(inner_parameters)

                t0 = time.time()
                agents_fitness, env_params = fitness(self.parameters_value, scenario,
                                                     meta={"chromosome_id": chromosome_id})

                strategy_fitness.append(agents_fitness)

                print("Model run once:", time.time() - t0, "param values:")
                assert np.isfinite(strategy_fitness).all(), f"Fitness contains infinite value {strategy_fitness}"

                for param_name, param_value in env_params.items():
                    env_parameters[param_name][chromosome_id] = param_value
            print("env_parameters", env_parameters)
            agent_parameters_mean = [
                {self.parameter_names[j] + "_mean": np.mean(agent_parameters[i][j]) for j in
                 range(self.params_each_agent)} for i
                in
                range(self.agent_num)
            ]
            agent_parameters_cov = [
                {self.parameter_names[j] + "_cov": np.std(agent_parameters[i][j]) / np.mean(agent_parameters[i][j]) for
                 j in
                 range(self.params_each_agent)} for i in range(self.agent_num)]
            strategy_fitness = np.array(strategy_fitness)

            fitness_mean = [float(np.mean(strategy_fitness[:, agent_id])) for agent_id in range(self.agent_num)]
            fitness_cov = [float(np.std(strategy_fitness[:, agent_id]) / np.mean(strategy_fitness[:, agent_id])) for
                           agent_id in range(self.agent_num)]

            env_params_mean = {param_name + "_mean": float(np.mean(param_value_list)) for param_name, param_value_list
                               in env_parameters.items()}
            env_params_cov = {param_name + "_cov": float(np.std(param_value_list) / np.mean(param_value_list)) for
                              param_name, param_value_list in
                              env_parameters.items()}
            meta = []
            for agent_id in range(self.agent_num):
                d = {'fitness_mean': fitness_mean[agent_id], "fitness_cov": fitness_cov[agent_id]}
                d.update(agent_parameters_mean[agent_id])
                d.update(agent_parameters_cov[agent_id])

                meta.append(d)
            env_params_meta = {}
            env_params_meta.update(env_params_mean)
            env_params_meta.update(env_params_cov)
            agents = yield strategy_population, params, strategy_fitness, {"agent_learning_cov": meta,
                                                                           "env_learning_cov": env_params_meta}
            for i in range(agents):
                strategy_population[:,
                i * self.strategy_param_code_length * self.params_each_agent:

                i * self.params_each_agent * self.strategy_param_code_length + self.params_each_agent * self.strategy_param_code_length] \
                    = ga.population_update(
                    strategy_population[:,
                    i * self.strategy_param_code_length * self.params_each_agent:
                    i * self.params_each_agent * self.strategy_param_code_length + self.params_each_agent * self.strategy_param_code_length],
                    strategy_fitness[:, i],
                    self.mutation_prob, self.strategy_population_size)


class ParticleSwarmOptimization(TrainingAlgorithm):
    pass


class Trainer(Simulator, abc.ABC):
    # 用来individually calibrate agents' parameters，
    # 只考虑针对strategy中参数的off-line learning。online-learning的部分千奇百怪，暂时交给用户自己来吧。
    def __init__(self, config: 'Config', scenario_class: 'Optional[ClassVar[Scenario]]',
                 model_class: 'Optional[ClassVar[Model]]'):
        super().__init__()
        self.config = config
        self.training_strategy: 'Optional[Type[TrainingAlgorithm]]' = None
        self.container_name: str = ''
        self.property_name: str = ''
        self.properties: List[str] = []

        self.environment_properties: List[str] = []

        self.algorithm: Optional[Type[TrainingAlgorithm]] = None
        self.algorithm_instance: Iterator[List[float]] = {}

        self.model_class: Optional[ClassVar[Model]] = model_class
        self.model: Optional[Model] = None
        self.scenario_class: Optional[ClassVar[Scenario]] = scenario_class

        self.agent_result_columns = [
            "scenario_id", "learning_scenario_id", "learning_path_id", "generation_id", "chromosome_id", "agent_id",
            "para_1", "para_2", "para_3", "fitness"
        ]
        self.agent_result = []

        self.current_algorithm_meta = {
            "scenario_id": 0,
            "learning_scenario_id": 1, "learning_path_id": 0, "generation_id": 0}

    def setup(self):
        pass

    def train(self):
        self.setup()
        self.pre_run()
        learning_scenarios_table = self.get_registered_dataframe('learning_scenarios')
        assert isinstance(learning_scenarios_table, pd.DataFrame), "No learning scenarios table specified!"

        for scenario in self.scenarios:
            self.current_algorithm_meta['scenario_id'] = scenario.id
            learning_scenarios = learning_scenarios_table.to_dict(orient="records")
            for learning_scenario in learning_scenarios:
                learning_scenario = GALearningScenario.from_dataframe_record(learning_scenario)
                self.current_algorithm_meta['learning_scenario_id'] = learning_scenario.id
                for learning_path_id in range(learning_scenario.number_of_path):
                    self.current_algorithm_meta['learning_path_id'] = learning_path_id

                    self.learn_once(scenario, learning_scenario)

    def learn_once(self, scenario, learning_scenario: GALearningScenario):

        scenario.manager = self
        self.model = self.model_class(self.config, scenario)
        self.model.setup()
        agents_num = len(self.model.__getattribute__(self.container_name))
        agents = self.model.__getattribute__(self.container_name)
        self.algorithm = GeneticAlgorithm(learning_scenario.training_generation, learning_scenario.strategy_population,
                                          learning_scenario.mutation_prob, learning_scenario.strategy_param_code_length)
        self.algorithm.set_parameters_agents(agents_num,
                                             len(self.properties),
                                             self.properties,
                                             self.environment_properties)
        self.algorithm.parameters = learning_scenario.get_parameters_range(agents_num)

        self.algorithm.parameters_value = []
        for agent in agents:
            self.algorithm.parameters_value.extend([agent.__getattribute__(name) for name in self.properties])

        self.algorithm_instance = self.algorithm.optimize_multi_agents(self.fitness, scenario)

        for i in range(learning_scenario.training_generation):
            self.current_algorithm_meta['generation_id'] = i
            print(f"===================Training step {i + 1}=====================")
            if i == 0:
                strategy_population, params, fitness, meta = self.algorithm_instance.__next__()
            else:
                strategy_population, params, fitness, meta = self.algorithm_instance.send(len(agents))
            agent_learning_cov = copy.deepcopy(meta['agent_learning_cov'])
            env_learning_cov = copy.deepcopy(meta['env_learning_cov'])

            for d in agent_learning_cov:
                d.update(self.current_algorithm_meta)
            env_learning_cov.update(self.current_algorithm_meta)
            create_db_conn(self.config).write_dataframe('agent_learning_cov', pd.DataFrame(agent_learning_cov))
            create_db_conn(self.config).write_dataframe('env_learning_cov', pd.DataFrame([env_learning_cov]))

            # params = np.sum(params, 0) / self.algorithm.strategy_population_size
        # df_l = []
        # for i in range(len(agents)):
        #     param_dict = {"agent_id": i}
        #     for j in range(len(self.properties)):
        #         param_dict[j] = params[len(self.properties) * i + j]
        #     df_l.append(param_dict)
        # df = pd.DataFrame(df_l)
        #

    def set_algorithm(self, algorithm: Type[TrainingAlgorithm]):
        """

        :param algorithm:
        :return:
        """
        assert isinstance(algorithm, TrainingAlgorithm)
        self.algorithm = algorithm

    def add_property(self, container: str, prop: str):
        """
        添加一个属性
        :param container:
        :param prop:
        :return:
        """
        assert prop not in self.properties
        self.container_name = container
        self.properties.append(prop)

    def get_agent_params(self, all_params, agent_id: int):
        agent_params = {}
        for j, prop_name in enumerate(self.properties):
            agent_params[prop_name] = all_params[agent_id * len(self.properties) + j]
        return agent_params

    def fitness(self, params, scenario: Union[Type[Scenario], Scenario], **kwargs) -> Tuple[np.ndarray, dict]:
        self.model = self.model_class(self.config, scenario)
        self.model.setup()
        agents = self.model.__getattribute__(self.container_name)
        agents_params_list = []
        environment_record_dict = {}
        environment_record_dict.update(self.current_algorithm_meta)

        for i, agent in enumerate(agents):
            agents_dic = {
                "agent_id": agent.id,
            }
            agents_dic.update(kwargs['meta'])
            agents_dic.update(self.current_algorithm_meta)
            assert i == agent.id
            agent_params = self.get_agent_params(params, agent.id)
            for j, prop_name in enumerate(self.properties):
                setattr(agent, prop_name, agent_params[prop_name])
            agents_dic.update(agent_params)
            agents_params_list.append(agents_dic)
        self.model.run()

        agents = self.model.__getattribute__(self.container_name)
        env = self.model.environment
        environment_properties_dict = {prop_name: env.__dict__[prop_name] for prop_name in self.environment_properties}
        environment_record_dict.update(environment_properties_dict)
        fitness_list = []
        for i, agent in enumerate(agents):
            agent_fitness = self.fitness_agent(agent)
            fitness_list.append(agent_fitness)
            agents_params_list[agent.id]['fitness'] = agent_fitness
        create_db_conn(self.config).write_dataframe('agent_learning_result', pd.DataFrame(agents_params_list),
                                                    if_exists="append")
        create_db_conn(self.config).write_dataframe('env_learning_result', pd.DataFrame([environment_record_dict]),
                                                    if_exists="append")
        return np.array(fitness_list), environment_properties_dict

    def fitness_agent(self, agent: Type[Agent]) -> float:
        """
        返回float，只要保证值越大、策略越好即可。
        无需保证>=0
        :param agent:
        :return:
        """
        pass
