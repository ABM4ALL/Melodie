# -*- coding:utf-8 -*-
# @Time: 2023/2/18 17:03
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: process.py
import abc
from typing import List
from .action import Action, IOPort


class Process(Action):
    def __init__(self):
        super().__init__()
        self.next_actions = []

    @abc.abstractmethod
    def outputs(self) -> List[IOPort]:
        pass

    def step(self, current_step: int):
        pass
