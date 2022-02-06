# -*- coding:utf-8 -*-
# @Time: 2021/12/20 9:27
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: ga.py
import logging
import math
import sys
import time
from abc import ABC
from typing import Callable, List, Type, Optional, TYPE_CHECKING

import numpy as np
import random

from Melodie.boost import JIT_AVAILABLE

logger = logging.getLogger(__name__)
if JIT_AVAILABLE:
    from numba import njit
else:
    from Melodie.boost import fake_jit

    njit = fake_jit
if TYPE_CHECKING:
    from Melodie import Scenario


@njit(cache=True)
def translate_binary2real(binary_array, min_value, max_value):
    sum = 0
    length = len(binary_array)
    real_maximum = 2 ** length - 1
    for bit in range(0, length):
        sum += binary_array[bit] * 2 ** (length - 1 - bit)
    real_value = min_value + sum / real_maximum * (max_value - min_value)
    return real_value


@njit(cache=True)
def prob_calculation(fitness_array):
    fitness_max = fitness_array.max()
    fitness_min = fitness_array.min()
    score_array = (fitness_array - fitness_min) / (fitness_max - fitness_min)
    score_sum = score_array.sum()
    prob_array = score_array / score_sum

    return prob_array


@njit(cache=True)
def gene_pick(prob_array, strategy_population):
    random_number = random.uniform(0, 1)
    accumulated_pick_probability = 0

    for strategy in range(0, strategy_population):

        accumulated_pick_probability += prob_array[strategy]
        if accumulated_pick_probability >= random_number:
            gene_picked_number = strategy
            break
        else:
            gene_picked_number = np.random.randint(strategy_population)

    return gene_picked_number


@njit(cache=True)
def crossover(gene_1, gene_2, probability_1, probability_2):
    probability = probability_1 / (probability_1 + probability_2)
    gene_new = np.zeros((len(gene_1),))

    for bit in range(0, len(gene_1)):
        random_number = random.uniform(0, 1)
        if random_number <= probability:
            gene_new[bit] = gene_1[bit]
        else:
            gene_new[bit] = gene_2[bit]

    return gene_new


@njit(cache=True)
def mutation(gene, mutation_prob):
    random_number = random.uniform(0, 1)
    if random_number <= mutation_prob:
        randint = random.randint(0, len(gene) - 1)
        if gene[randint] == 0:
            gene[randint] = 1
        else:
            gene[randint] = 0
    else:
        pass

    return gene


@njit(cache=True)
def population_update(population, fitness_array, mutation_prob, population_scale):
    strategy_population = population_scale

    prob_array = prob_calculation(fitness_array)
    population_new = np.zeros(population.shape)
    strategy_number_list = np.array([i for i in range(0, strategy_population)])
    random.shuffle(strategy_number_list)

    for strategy in range(0, strategy_population):
        gene_1_number = gene_pick(prob_array, strategy_population)
        gene_2_number = gene_pick(prob_array, strategy_population)
        gene_1 = population[gene_1_number]
        gene_2 = population[gene_2_number]

        gene_new = crossover(gene_1,
                             gene_2,
                             prob_array[gene_1_number],
                             prob_array[gene_2_number])

        gene_new = mutation(gene_new, mutation_prob)

        population_new[strategy_number_list[strategy]] = gene_new

    return population_new


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
                 number_of_generation: int,
                 strategy_population_size: int,
                 mutation_prob: float,
                 strategy_param_code_length: int, ):
        self.number_of_generation: int = number_of_generation
        self.strategy_population_size = strategy_population_size
        self.mutation_prob = mutation_prob
        self.strategy_param_code_length = strategy_param_code_length
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
        self.parameters_num = self.agent_num * self.params_each_agent
        self.parameters = [(-5, 5) for i in range(self.parameters_num)]
        self.parameters_value = np.array([1 for i in range(self.parameters_num)], dtype=np.float64)
        self.parameter_names = parameter_names
        self.env_property_names = env_property_names

    def agent_params_convertion(self):
        pass

    def optimize(self, fitness: Callable, scenario):
        """

        :param fitness:
        :return:
        """
        strategy_population = np.random.randint(2,
                                                size=(self.strategy_population_size,
                                                      self.strategy_param_code_length * self.parameters_num))
        for gen in range(0, self.number_of_generation):
            strategy_fitness = []
            parameter_values: List[List[int]] = []
            for i, strategy in enumerate(strategy_population):
                inner_parameters: List[int] = []
                parameters_value = [0 for i in range(self.parameters_num)]
                for param_index in range(self.parameters_num):
                    parameters_value[param_index] = translate_binary2real(
                        strategy[param_index * self.strategy_param_code_length:
                                 (param_index + 1) * self.strategy_param_code_length],
                        self.parameters[param_index][0],
                        self.parameters[param_index][1]
                    )
                    inner_parameters.append(parameters_value[param_index])
                parameter_values.append(inner_parameters)

                strategy_fitness.append(fitness(parameters_value, scenario, meta={"chromosome_id": i}))
                assert np.isfinite(strategy_fitness).all(), f"Fitness contains infinite value {strategy_fitness}"
            parameter_values_arr = np.array(parameter_values)
            fitness_mean = np.mean(strategy_fitness)
            fitness_cov = np.std(strategy_fitness) / np.mean(strategy_fitness)

            env_params_mean = {self.parameter_names[index] + "_mean": float(np.mean(parameter_values_arr[:, index])) for
                               index
                               in range(parameter_values_arr.shape[1])}
            env_params_cov = {self.parameter_names[index] + "_cov": float(
                np.std(parameter_values_arr[:, index]) / np.mean(parameter_values_arr[:, index])) for
                index in range(parameter_values_arr.shape[1])}
            yield strategy_population, parameter_values, strategy_fitness, {'env_params_mean': env_params_mean,
                                                                            'env_params_cov': env_params_cov,
                                                                            'fitness_cov': fitness_cov,
                                                                            'fitness_mean': fitness_mean}

            strategy_population = population_update(strategy_population, np.array(strategy_fitness),
                                                    self.mutation_prob, self.strategy_population_size)

    def optimize_multi_agents(self, fitness: Callable, scenario: Type['Scenario']):
        """
        Optimization for multi-agent system.
        :param fitness:
        :param scenario:
        :return:
        """
        strategy_population = np.random.randint(2,
                                                size=(self.strategy_population_size,
                                                      self.strategy_param_code_length * self.parameters_num))
        for gen in range(0, self.number_of_generation):
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
                    self.parameters_value[param_index] = translate_binary2real(
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

                logger.debug(f"Model run once took {time.time() - t0}s")
                assert np.isfinite(strategy_fitness).all(), f"Fitness contains infinite value {strategy_fitness}"

                for param_name, param_value in env_params.items():
                    env_parameters[param_name][chromosome_id] = param_value

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
                d = {'agent_id': agent_id, 'fitness_mean': fitness_mean[agent_id], "fitness_cov": fitness_cov[agent_id]}
                d.update(agent_parameters_mean[agent_id])
                d.update(agent_parameters_cov[agent_id])

                meta.append(d)
            env_params_meta = {}
            env_params_meta.update(env_params_mean)
            env_params_meta.update(env_params_cov)
            agents = yield strategy_population, params, strategy_fitness, {"agent_trainer_result_cov": meta,
                                                                           "env_trainer_result_cov": env_params_meta}
            for i in range(agents):
                strategy_population[:,
                i * self.strategy_param_code_length * self.params_each_agent:

                i * self.params_each_agent * self.strategy_param_code_length + self.params_each_agent * self.strategy_param_code_length] \
                    = population_update(
                    strategy_population[:,
                    i * self.strategy_param_code_length * self.params_each_agent:
                    i * self.params_each_agent * self.strategy_param_code_length + self.params_each_agent * self.strategy_param_code_length],
                    strategy_fitness[:, i],
                    self.mutation_prob, self.strategy_population_size)


class ParticleSwarmOptimization(TrainingAlgorithm):
    pass


if __name__ == "__main__":
    def loss_function(x1, x2):
        y_target = 0
        # y_x = 3 * x1 ** 2 + 5 * x2 ** 2
        y_x = 3 * x1 ** 2 + np.sin(x2) ** 2
        return abs(y_target - y_x)  # solution: x = 3


    def fitness_function(loss):
        # 就是为了把loss变成“正向/越大越好”的fitness，没有直接用1/loss而是求2**loss，是为了避免loss等于0报错
        # 但是2**loss容易造成数据向负方向溢出。
        return 1 / (2 * abs(loss) + 1)
        # return 1 / 2 ** loss


    GeneticAlgorithm(100, 100, 0.02, 20).optimize(loss_function, fitness_function)
