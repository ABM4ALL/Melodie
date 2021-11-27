# -*- coding:utf-8 -*-
# @Time: 2021/11/11 10:39
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: test_grid.py
import json
import random
import sys
import time

import numba
import numpy as np

from Melodie import AgentList, Agent
from Melodie.network import Network, build_jit_class
import logging

from .config import model

logger = logging.getLogger(__name__)

N = 10000_000


def test_network():
    n = Network()
    n.add_edge(0, 1)
    n.add_edge(0, 2)
    n.add_edge(0, 3)
    n.add_edge(0, 4)
