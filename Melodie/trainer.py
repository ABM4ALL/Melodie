import abc
import time
from typing import Type, Callable, List, Optional, ClassVar, Dict, Iterator
from abc import ABC, abstractmethod

import numpy as np
import pandas as pd

from Melodie import Model, Scenario, Simulator, Config, Agent
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

    def optimize_multi_agents(self):
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

    def set_parameters_agents(self, agent_num: int, agent_params: int):

        self.params_each_agent = agent_params
        self.agent_num = agent_num
        self.parameters_num = self.agent_num * self.params_each_agent  # 参数的数量
        self.parameters = [(-5, 5) for i in range(self.parameters_num)]
        self.parameters_value = np.array([1 for i in range(self.parameters_num)], dtype=np.float64)

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

                strategy_fitness.append(fitness(self.parameters_value))
                assert np.isfinite(strategy_fitness).all(), f"Fitness contains infinite value {strategy_fitness}"

            print("(", end="")
            for param_index in range(self.parameters_num):
                print(str(round(parameter_sums[param_index] / self.strategy_population_size, self.params_each_agent)),
                      end=", ")
            print(")")
            ret = yield strategy_population, parameter_values, strategy_fitness
            if ret is None:
                strategy_population = ga.population_update(strategy_population, strategy_fitness,
                                                           self.mutation_prob, self.strategy_population_size)
            else:
                assert ret.shape == strategy_population.shape
                strategy_population = ret

    def optimize_multi_agents(self, fitness: Callable):
        """
        Optimization for multi-agent system.
        :param fitness:
        :return:
        """
        strategy_population = np.random.randint(2,
                                                size=(self.strategy_population_size,
                                                      self.strategy_param_code_length * self.parameters_num))
        for gen in range(0, self.training_generations):
            strategy_fitness = []
            parameter_sums = [0 for i in range(len(self.parameters))]
            params: List[List[int]] = []
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
                params.append(inner_parameters)

                strategy_fitness.append(fitness(self.parameters_value))
                assert np.isfinite(strategy_fitness).all(), f"Fitness contains infinite value {strategy_fitness}"

            print("(", end="")
            for param_index in range(self.parameters_num):
                print(str(round(parameter_sums[param_index] / self.strategy_population_size, self.params_each_agent)),
                      end=", ")
            print(")")

            print(strategy_fitness)
            strategy_fitness = np.array(strategy_fitness)
            agents = yield strategy_population, params, strategy_fitness
            print(strategy_population.shape, len(params), strategy_fitness.shape, )
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
            print(i * self.strategy_param_code_length * self.params_each_agent)


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
        self.algorithm: Optional[Type[TrainingAlgorithm]] = None
        self.algorithm_instance: Iterator[List[float]] = {}

        self.model_class: Optional[ClassVar[Model]] = model_class
        self.model: Optional[Model] = None
        self.scenario_class: Optional[ClassVar[Scenario]] = scenario_class
        self.scenario: Optional[Scenario] = None

    def setup(self):
        pass

    def train(self):
        self.register_scenario_dataframe()
        self.register_static_dataframes()
        self.register_generated_dataframes()
        self.setup()
        self.scenario = self.scenario_class(0)
        self.scenario.manager = self
        self.model = self.model_class(self.config, self.scenario)
        self.model.setup()
        agents_num = len(self.model.__getattribute__(self.container_name))
        agents = self.model.__getattribute__(self.container_name)
        strategy_param_code_length = 10
        genes = 10
        self.algorithm.set_parameters_agents(agents_num, len(self.properties))
        self.algorithm.parameters = [(0, 100) for i in range(len(self.properties) * len(agents))]
        self.algorithm.parameters_value = []
        for agent in agents:
            self.algorithm.parameters_value.extend([agent.__getattribute__(name) for name in self.properties])

        self.algorithm_instance = self.algorithm.optimize_multi_agents(self.fitness)

        def cov(x):
            x = np.array(x)
            return (np.std(x) / np.mean(x)).tolist()

        l = []
        covs_agents = []
        for i in range(20):
            if i == 0:
                strategy_population, params, fitness = self.algorithm_instance.__next__()
            else:
                strategy_population, params, fitness = self.algorithm_instance.send(len(agents))
            fitness = np.array(fitness)

            param_this_step = [
                [(params[j][i * len(self.properties)], params[j][i * len(self.properties) + 1],
                  params[j][i * len(self.properties) + 2])
                 for i in range(agents_num)] for j in
                range(genes)]
            l.append(param_this_step)
            covs_agents.append([
                (cov([param_this_step[j][i][0] for j in range(genes)]),
                 cov([param_this_step[j][i][1] for j in range(genes)]),
                 cov([param_this_step[j][i][2] for j in range(genes)]))
                for i in range(len(param_this_step[0]))])
            print(strategy_population.shape, len(params), fitness.shape, )

            print(i * strategy_param_code_length * len(self.properties))

        params = np.sum(params, 0) / self.algorithm.strategy_population_size
        df_l = []
        for i in range(len(agents)):
            param_dict = {"agent_id": i}
            for j in range(len(self.properties)):
                param_dict[j] = params[len(self.properties) * i + j]
            df_l.append(param_dict)
        df = pd.DataFrame(df_l)
        print(df)

        df.to_csv(f"agent_params.csv")
        import json
        with open("param_agents.json", 'w') as f:
            json.dump(l, f, indent=4)
        with open("cov_agents.json", 'w') as f:
            json.dump(covs_agents, f, indent=4)

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

    def fitness(self, params) -> float:
        self.scenario = self.scenario_class(0)
        self.scenario.manager = self
        self.model = self.model_class(self.config, self.scenario)
        self.model.setup()
        agents = self.model.__getattribute__(self.container_name)
        for i, agent in enumerate(agents):
            for j, prop_name in enumerate(self.properties):
                setattr(agent, prop_name, params[i * len(self.properties) + j])
        self.model.run()
        fitness_list = []
        for agent in agents:
            fitness_list.append(self.fitness_agent(agent))
        return np.array(fitness_list)

    def fitness_agent(self, agent: Type[Agent]):
        return agent.account


if __name__ == "__main__":
    def loss_function(x):
        y_target = 0
        # y_x = 3 * x1 ** 2 + 5 * x2 ** 2
        y_x = 3 * x[0] ** 2 + np.sin(x[1]) ** 2
        return abs(y_target - y_x)  # solution: x = 3


    def fitness_function(loss):
        # 就是为了把loss变成“正向/越大越好”的fitness，没有直接用1/loss而是求2**loss，是为了避免loss等于0报错
        # 但是2**loss容易造成数据向负方向溢出。
        return 1 / (2 * abs(loss) + 1)
        # return 1 / 2 ** loss


    def f():
        i = 0
        while 1:
            res = yield i
            i += 1
            print('res', res)


    opt = GeneticAlgorithm(100, 100, 0.02, 20, 2).optimize(loss_function, fitness_function)
    while 1:
        try:
            print(next(opt))
        except StopIteration:
            break
