# -*- coding:utf-8 -*-
# @Time: 2023/2/18 17:03
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: action.py
import abc
from typing import List
from ..lowcode.params import ParamsManager


class IOPort:
    def __init__(self, name: str):
        self.name = name

    def to_json_dumpable(self):
        return self.__dict__


class Action(abc.ABC):

    def __init__(self):
        self.name = 'base_action'
        self.next_actions: List[Action] = []

    @abc.abstractmethod
    def on_entry(self, current_step: int):
        raise NotImplementedError

    @abc.abstractmethod
    def step(self, current_step: int):
        raise NotImplementedError

    def title(self):
        return self.__class__.__name__

    @abc.abstractmethod
    def parameters_manager(self) -> ParamsManager:
        raise NotImplementedError

    @abc.abstractmethod
    def inputs(self) -> List[IOPort]:
        raise NotImplementedError

    @abc.abstractmethod
    def outputs(self) -> List[IOPort]:
        raise NotImplementedError

    def to_desc_json_dumpable(self):
        return {
            "name": self.name,
            "title": self.title(),
            "formModel": self.parameters_manager().to_form_model(),
            "outputs": [port.to_json_dumpable() for port in self.outputs()]
        }


class Terminated:
    pass
