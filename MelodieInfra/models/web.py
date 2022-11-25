# -*- coding:utf-8 -*-
# @Time: 2022/11/23 22:03
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: web.py.py
import json
from dataclasses import dataclass
from enum import Enum
from typing import Any


class DataServiceState(int, Enum):
    SUCCESS = 0
    ERROR = 1


@dataclass
class DataServiceStatus:
    status: DataServiceState
    msg: str = ""
    data: Any = None

    def to_json(self):
        return json.dumps({"msg": self.msg, "data": self.data, "status": self.status})
