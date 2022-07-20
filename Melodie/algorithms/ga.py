import logging
import math
import time
from typing import (
    Callable,
    List,
    Type,
    Optional,
    TYPE_CHECKING,
    Dict,
    Union,
    Tuple,
    Any,
)

import numpy as np
import random

import pandas as pd
from sko.GA import GA

from .searching_algorithm import SearchingAlgorithm, AlgorithmParameters

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from Melodie import Scenario


# @njit(cache=True)
def translate_binary2real(binary_array, min_value, max_value):
    sum = 0
    length = len(binary_array)
    real_maximum = 2**length - 1
    for bit in range(0, length):
        sum += binary_array[bit] * 2 ** (length - 1 - bit)
    real_value = min_value + sum / real_maximum * (max_value - min_value)
    return real_value


# @njit(cache=True)
def prob_calculation(fitness_array):
    fitness_max = fitness_array.max()
    fitness_min = fitness_array.min()
    score_array = (fitness_array - fitness_min) / (fitness_max - fitness_min)
    score_sum = score_array.sum()
    prob_array = score_array / score_sum

    return prob_array


def gene_pick(prob_array, strategy_population):
    """

    :param prob_array:
    :param strategy_population:
    :return:
    """
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

        gene_new = crossover(
            gene_1, gene_2, prob_array[gene_1_number], prob_array[gene_2_number]
        )

        gene_new = mutation(gene_new, mutation_prob)

        population_new[strategy_number_list[strategy]] = gene_new

    return population_new


class GATrainerParams(AlgorithmParameters):
    def __init__(
        self,
        id: int,
        number_of_path: int,
        number_of_generation: int,
        strategy_population: int,
        mutation_prob: float,
        strategy_param_code_length: int,
        **kw,
    ):
        super().__init__(id, number_of_path)
        self.number_of_generation = number_of_generation
        self.strategy_population = strategy_population
        self.mutation_prob = mutation_prob
        self.strategy_param_code_length = strategy_param_code_length
        self.parse_params(kw)

    @staticmethod
    def from_dataframe_record(
        record: Dict[str, Union[int, float]]
    ) -> "GATrainerParams":
        s = GATrainerParams(
            record["id"],
            record["number_of_path"],
            record["number_of_generation"],
            record["strategy_population"],
            record["mutation_prob"],
            record["strategy_param_code_length"],
        )
        s.parse_params(record)
        return s

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.__dict__}>"

    def __hash__(self):
        return hash(
            (
                self.id,
                self.number_of_path,
                self.number_of_generation,
                self.strategy_population,
                self.mutation_prob,
                self.strategy_param_code_length,
            )
        )


class GACalibratorParams(AlgorithmParameters):
    def __init__(
        self,
        id: int,
        number_of_path: int,
        number_of_generation: int,
        strategy_population: int,
        mutation_prob: int,
        strategy_param_code_length: int,
        **kw,
    ):
        super().__init__(id, number_of_path)

        self.number_of_generation = number_of_generation
        self.strategy_population = strategy_population
        self.mutation_prob = mutation_prob
        self.strategy_param_code_length = strategy_param_code_length
        self.parse_params(kw)

    @staticmethod
    def from_dataframe_record(
        record: Dict[str, Union[int, float]]
    ) -> "GACalibratorParams":
        s = GACalibratorParams(
            record["id"],
            record["number_of_path"],
            record["number_of_generation"],
            record["strategy_population"],
            record["mutation_prob"],
            record["strategy_param_code_length"],
        )
        s.parse_params(record)
        return s

    def __hash__(self):
        return hash(
            (
                self.id,
                self.number_of_path,
                self.number_of_generation,
                self.strategy_population,
                self.mutation_prob,
                self.strategy_param_code_length,
            )
        )


class GeneticAlgorithmTrainer(SearchingAlgorithm):
    def __init__(
        self,
        number_of_generation: int,
        strategy_population_size: int,
        mutation_prob: float,
        strategy_param_code_length: int,
    ):
        self.number_of_generation: int = number_of_generation
        self.strategy_population_size = strategy_population_size
        self.mutation_prob = mutation_prob
        self.strategy_param_code_length = strategy_param_code_length

        self.agent_num = 0
        self.params_each_agent = 0
        self.parameters_range = []
        self.parameters_value: Optional[np.ndarray] = None
        self.parameter_names = []
        self.env_property_names = []
        self.agent_result_properties: List[str] = []

    def set_parameters_agents(
        self,
        agent_num: int,
        agent_params: int,
        parameter_names: List[str],
        agent_result_properties: List[str],
        env_property_names: List[str],
    ):
        """

        :param agent_num:
        :param agent_params:
        :param parameter_names:
        :param agent_result_properties:
        :param env_property_names:
        :return:
        """

        self.params_each_agent = agent_params
        self.agent_num = agent_num
        parameters_num = self.agent_num * self.params_each_agent
        self.parameters_range = [(-5, 5) for i in range(parameters_num)]
        self.parameters_value = np.array(
            [1 for i in range(parameters_num)], dtype=np.float64
        )
        self.parameter_names = parameter_names
        self.env_property_names = env_property_names
        self.agent_result_properties = agent_result_properties

    def agent_params_convertion(self):
        pass

    def calc_agents_mean_and_cov(self, agent_props_each_chromosome: List[dict]):
        df = pd.DataFrame(agent_props_each_chromosome)
        df.head()

        def calc_cov(series: pd.Series):
            return series.std() / series.mean()

        param_names_to_collect = self.parameter_names + self.agent_result_properties
        agent_parameters_mean = [
            {
                name + "_mean": df[df["agent_id"] == agent_id][name].mean()
                for name in param_names_to_collect
            }
            for agent_id in range(self.agent_num)
        ]
        agent_parameters_cov = [
            {
                name + "_cov": calc_cov(df[df["agent_id"] == agent_id][name])
                for name in param_names_to_collect
            }
            for agent_id in range(self.agent_num)
        ]
        return agent_parameters_mean, agent_parameters_cov

    def calc_env_mean_and_cov(self, env_parameters: dict):
        env_params_mean = {
            param_name + "_mean": float(np.mean(param_value_list))
            for param_name, param_value_list in env_parameters.items()
        }
        env_params_cov = {
            param_name
            + "_cov": float(np.std(param_value_list) / np.mean(param_value_list))
            for param_name, param_value_list in env_parameters.items()
        }
        return env_params_mean, env_params_cov

    def optimize_multi_agents(self, fitness: Callable, scenario: Type["Scenario"]):
        """
        Optimization for multi-agent system.
        :param fitness:
        :param scenario:
        :return:
        """
        strategy_population = np.random.randint(
            2,
            size=(
                self.strategy_population_size,
                self.strategy_param_code_length
                * self.agent_num
                * self.params_each_agent,
            ),
        )

        for gen in range(0, self.number_of_generation):
            strategy_fitness = []
            agent_props_each_chromosome = []
            parameter_sums = [0 for i in range(len(self.parameters_range))]
            params: List[List[int]] = []
            agent_parameters = [
                [
                    [0.0 for j in range(self.strategy_population_size)]
                    for k in range(self.params_each_agent)
                ]
                for i in range(self.agent_num)
            ]
            env_parameters = {
                env_parameter_name: [0 for chromosome_id in strategy_population]
                for env_parameter_name in self.env_property_names
            }
            for chromosome_id, strategy in enumerate(strategy_population):
                inner_parameters: List[int] = []
                for param_index in range(self.agent_num * self.params_each_agent):
                    self.parameters_value[param_index] = translate_binary2real(
                        strategy[
                            param_index
                            * self.strategy_param_code_length : (param_index + 1)
                            * self.strategy_param_code_length
                        ],
                        self.parameters_range[param_index][0],
                        self.parameters_range[param_index][1],
                    )
                    parameter_sums[param_index] += self.parameters_value[param_index]
                    inner_parameters.append(self.parameters_value[param_index])
                    agent_index = math.floor(param_index / self.params_each_agent)
                    param_index_in_agent_params = param_index % self.params_each_agent

                    agent_parameters[agent_index][param_index_in_agent_params][
                        chromosome_id
                    ] = self.parameters_value[param_index]

                params.append(inner_parameters)

                t0 = time.time()

                agents_fitness, env_params, agent_props_list = fitness(
                    self.parameters_value,
                    scenario,
                    meta={"chromosome_id": chromosome_id},
                )

                print(agents_fitness, env_params, agent_props_list)
                strategy_fitness.append(agents_fitness)
                agent_props_each_chromosome.extend(agent_props_list)

                logger.debug(f"Model run once took {time.time() - t0}s")
                assert np.isfinite(
                    strategy_fitness
                ).all(), f"Fitness contains infinite value {strategy_fitness}"

                for param_name, param_value in env_params.items():
                    env_parameters[param_name][chromosome_id] = param_value

            strategy_fitness = np.array(strategy_fitness)
            agent_parameters_mean, agent_parameters_cov = self.calc_agents_mean_and_cov(
                agent_props_each_chromosome
            )

            env_params_mean, env_params_cov = self.calc_env_mean_and_cov(env_parameters)
            agent_trainer_result_cov = []
            for agent_id in range(self.agent_num):
                d = {"agent_id": agent_id}
                d.update(agent_parameters_mean[agent_id])
                d.update(agent_parameters_cov[agent_id])

                agent_trainer_result_cov.append(d)
            env_params_meta = {}
            env_params_meta.update(env_params_mean)
            env_params_meta.update(env_params_cov)
            agents_num = (
                yield strategy_population,
                params,
                strategy_fitness,
                {
                    "agent_trainer_result_cov": agent_trainer_result_cov,
                    "env_trainer_result_cov": env_params_meta,
                },
            )
            for i in range(agents_num):
                strategy_population[
                    :,
                    i
                    * self.strategy_param_code_length
                    * self.params_each_agent : i
                    * self.params_each_agent
                    * self.strategy_param_code_length
                    + self.params_each_agent * self.strategy_param_code_length,
                ] = population_update(
                    strategy_population[
                        :,
                        i
                        * self.strategy_param_code_length
                        * self.params_each_agent : i
                        * self.params_each_agent
                        * self.strategy_param_code_length
                        + self.params_each_agent * self.strategy_param_code_length,
                    ],
                    strategy_fitness[:, i],
                    self.mutation_prob,
                    self.strategy_population_size,
                )


class GeneticAlgorithmCalibrator(SearchingAlgorithm):
    def __init__(
        self,
        number_of_generation: int,
        strategy_population_size: int,
        mutation_prob: float,
        strategy_param_code_length: int,
    ):
        self.number_of_generation: int = number_of_generation
        self.strategy_population_size = strategy_population_size
        self.mutation_prob = mutation_prob
        self.strategy_param_code_length = strategy_param_code_length
        self.agent_num = 0
        self.params_each_agent = 0
        self.parameters_num = 0
        self.parameters_range = []
        self.parameters_value: Optional[np.ndarray] = None
        self.parameter_names = []
        self.env_property_names = []
        self.agent_result_properties: List[str] = []

    def agent_params_convertion(self):
        pass

    def optimize(self, fitness: "Callable[[Any, Scenario], Tuple[int, int]]", scenario):
        """

        :param fitness:
        :param scenario:
        :return:
        """
        strategy_population = np.random.randint(
            2,
            size=(
                self.strategy_population_size,
                self.strategy_param_code_length * self.parameters_num,
            ),
        )
        for gen in range(0, self.number_of_generation):
            strategy_fitness = []
            strategy_distance = []
            parameter_values: List[List[int]] = []
            for i, strategy in enumerate(strategy_population):
                inner_parameters: List[int] = []
                parameters_value = [0 for i in range(self.parameters_num)]
                for param_index in range(self.parameters_num):
                    parameters_value[param_index] = translate_binary2real(
                        strategy[
                            param_index
                            * self.strategy_param_code_length : (param_index + 1)
                            * self.strategy_param_code_length
                        ],
                        self.parameters_range[param_index][0],
                        self.parameters_range[param_index][1],
                    )
                    inner_parameters.append(parameters_value[param_index])
                parameter_values.append(inner_parameters)
                fitness_value, distance_value = fitness(
                    parameters_value, scenario, meta={"chromosome_id": i}
                )
                strategy_fitness.append(fitness_value)
                strategy_distance.append(distance_value)
                assert np.isfinite(
                    strategy_fitness
                ).all(), f"Fitness contains infinite value {strategy_fitness}"
            parameter_values_arr = np.array(parameter_values)

            distance_mean = np.mean(strategy_distance)
            distance_cov = np.std(strategy_distance) / np.mean(strategy_distance)
            env_params_mean = {
                self.parameter_names[index]
                + "_mean": float(np.mean(parameter_values_arr[:, index]))
                for index in range(parameter_values_arr.shape[1])
            }
            env_params_cov = {
                self.parameter_names[index]
                + "_cov": float(
                    np.std(parameter_values_arr[:, index])
                    / np.mean(parameter_values_arr[:, index])
                )
                for index in range(parameter_values_arr.shape[1])
            }
            yield strategy_population, parameter_values, strategy_fitness, {
                "env_params_mean": env_params_mean,
                "env_params_cov": env_params_cov,
                "distance_cov": distance_cov,
                "distance_mean": distance_mean,
            }

            strategy_population = population_update(
                strategy_population,
                np.array(strategy_fitness),
                self.mutation_prob,
                self.strategy_population_size,
            )


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
