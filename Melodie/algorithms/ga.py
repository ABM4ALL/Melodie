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
