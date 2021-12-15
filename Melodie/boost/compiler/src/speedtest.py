# -*- coding:utf-8 -*-
# @Time: 2021/12/13 11:36
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: speedtest.py.py
import time

import numba
import abc
from numba.experimental import jitclass

import random
import numpy as np
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from Melodie import AgentList

if 1 < 0:
    from .ast_demo import Agent


class TechnologySearchStrategy(ABC):

    def __init__(self, agent_list: 'AgentList', environment: 'AspirationEnvironment'):
        self.agent_list = agent_list
        self.environment = environment

    @abstractmethod
    def technology_search(self, agent: 'AspirationAgent') -> None:
        pass


class SleepTechnologySearchStrategy(TechnologySearchStrategy):

    def technology_search(self, agent: 'AspirationAgent') -> None:
        agent.sleep_count += 1
        pass


class ExploitationTechnologySearchStrategy(TechnologySearchStrategy):

    def technology_search(self, agent: 'AspirationAgent') -> None:
        sigma = self.environment.sigma_exploitation
        technology_search_result = np.random.normal(agent.technology, sigma)
        agent.technology = max(agent.technology, technology_search_result)
        agent.exploitation_count += 1
        pass


class ExplorationTechnologySearchStrategy(TechnologySearchStrategy):

    def technology_search(self, agent: 'AspirationAgent') -> None:
        mean = self.environment.sigma_exploration
        sigma = self.environment.sigma_exploration
        technology_search_result = np.random.lognormal(mean, sigma)
        agent.technology = max(agent.technology, technology_search_result)
        agent.exploration_count += 1
        pass


class ImitationTechnologySearchStrategy(TechnologySearchStrategy):

    def technology_search(self, agent: 'AspirationAgent') -> None:
        random_agent_list = random.sample(self.agent_list, int(len(self.agent_list) * self.environment.imitation_share))
        technology_search_result = np.array([item.technology for item in random_agent_list]).max()
        rand = np.random.uniform(0, 1)
        if rand <= self.environment.imitation_success_rate:
            agent.technology = max(agent.technology, technology_search_result)
        else:
            pass
        agent.imitation_count += 1


from Melodie.boost.compiler.class_compiler import compile_general_class
from Melodie.boost.compiler.typeinferlib import register_type
from Melodie.boost.compiler.import_scanner import scan_imports, import_statements_to_str

# from
# register_type(TechnologySearchStrategy)
# compile_general_class(ImitationTechnologySearchStrategy)

imports = scan_imports(__file__)
print(imports)
print(import_statements_to_str(imports))