from math import floor
import random as random_module
from functools import lru_cache
from random import randint
import numpy as np


def iterable(a):
    return a


def new(a):
    return a


def _random():
    return random_module.random()


def set_seed(seed: int):
    random_module.seed(seed)
    np.random.seed(seed)
    # srand(seed)
