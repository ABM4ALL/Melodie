# -*- coding:utf-8 -*-
# @Time: 2021/12/20 9:27
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: ga.py
import sys
from typing import Callable

import numba
import numpy as np
import random

from Melodie.boost import JIT_AVAILABLE

if JIT_AVAILABLE:
    from numba import njit
else:
    from Melodie.boost import fake_jit

    njit = fake_jit


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


class GeneticAlgorithm():
    def __init__(self, training_generations: int,
                 strategy_population_size: int,
                 mutation_prob: float,
                 strategy_param_code_length: int):
        self.training_generations: int = training_generations
        self.strategy_population_size = strategy_population_size
        self.mutation_prob = mutation_prob  # 突变为了避免收敛到局部最优，但太大的导致搜索不稳定
        self.strategy_param_code_length = strategy_param_code_length  # 这个值越大解的精度越高 --> 把下面区间[strategy_param_min, strategy_param_max]分得越细

        self.parameters_num = 2  # 参数的数量
        self.parameters = [(-5, 5), (-5, 5)]
        self.parameters_value = np.array([1, 1])

    def optimize(self, loss: Callable, fitness: Callable):
        strategy_population = np.random.randint(2,
                                                size=(self.strategy_population_size,
                                                      self.strategy_param_code_length * self.parameters_num))
        for gen in range(0, self.training_generations):
            strategy_fitness = np.zeros((self.strategy_population_size,))
            parameter_sums = [0 for i in range(len(self.parameters))]
            for i, strategy in enumerate(strategy_population):
                for param_index in range(self.parameters_num):
                    self.parameters_value[param_index] = translate_binary2real(
                        strategy[
                        param_index * self.strategy_param_code_length:
                        (param_index + 1) * self.strategy_param_code_length],
                        self.parameters[param_index][0],
                        self.parameters[param_index][1])
                    parameter_sums[param_index] += self.parameters_value[param_index]
                # x_sum += x
                strategy_fitness[i] = fitness(loss(*self.parameters_value))
                assert np.isfinite(strategy_fitness).all(), f"Fitness contains infinite value {strategy_fitness}"

            print("(", end="")
            for param_index in range(self.parameters_num):
                print(str(round(parameter_sums[param_index] / self.strategy_population_size, 3)), end=", ")
            print(")")
            strategy_population = population_update(strategy_population, strategy_fitness,
                                                    self.mutation_prob, self.strategy_population_size)


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
