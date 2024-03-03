import random as random_module
from functools import lru_cache
from math import floor
from random import randint


def iterable(a):
    return a


def new(a):
    return a


def _random():
    return random_module.random()


def set_seed(seed: int):
    random_module.seed(seed)
    try:
        import numpy as np

        np.random.seed(seed)
    except ImportError:
        pass
    # srand(seed)
