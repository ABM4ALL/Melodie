# -*- coding:utf-8 -*-
# @Time: 2021/12/11 10:11
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: _config.py
from typing import Optional

from ..config import Config

_studio_config: Optional[Config] = None


def set_studio_config(config: Config):
    global _studio_config
    _studio_config = config


def get_studio_config() -> Config:
    return _studio_config
