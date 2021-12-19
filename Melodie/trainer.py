
from typing import Type
from abc import ABC, abstractmethod

"""
training strategy interface
"""
class TrainingStrategy(ABC):
    pass

class GeneticAlgorithmTrainingStrategy(TrainingStrategy):
    pass

class ParticleOptimizationTrainingStrategy(TrainingStrategy):
    pass

"""
trainer
"""
class Trainer:
    # 用来individually calibrate agents' parameters，
    # 只考虑针对strategy中参数的off-line learning。online-learning的部分千奇百怪，暂时交给用户自己来吧。

    def train(self, strategy: 'Type[TrainingStrategy]' = GeneticAlgorithmTrainingStrategy):
        pass
