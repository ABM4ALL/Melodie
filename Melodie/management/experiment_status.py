# -*- coding:utf-8 -*-
# @Time: 2021/10/25 15:11
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: simulation_status.py
import json
from typing import List, Tuple, Optional


class ExperimentStatus:
    def __init__(self, **kwargs):
        # Current status running now. If there are
        self.finished_run_ids: List[Optional[Tuple[int, int]]] = None
        self.current_run_ids: List[Optional[Tuple[int, int]]] = None
        self.waiting_run_ids: List[Optional[Tuple[int, int]]] = None
        # self.current_run_ids = None
        for kwarg, value in kwargs.items():
            assert kwarg in self.__dict__
            self.__dict__[kwarg] = value

    def to_json(self) -> str:
        return json.dumps(self.__dict__)
