# -*- coding:utf-8 -*-
# @Time: 2021/11/16 9:45
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: test_configs.py
import os.path

from Melodie.studio.config_manager import ConfigureCategory, ConfigureManager


class ReadonlyConfigCategory(ConfigureCategory):

    def setup(self):
        self.CHART_STYLE_CONFIG_FILE = "xxx"
        self.CHART_POLICIES_CONFIG_FILE = "yyy"


def test_config_readonly():
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'json', "config_readonly.json")
    category1 = ReadonlyConfigCategory(path)
    try:
        category1.CHART_POLICIES_CONFIG_FILE = "/home/user/cfg.json"
    except PermissionError:
        pass


def test_config_read_write():
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'json', "config_read_write.json")
    if os.path.exists(path):
        os.remove(path)
    category1 = ReadonlyConfigCategory(path, False)
    category1.CHART_POLICIES_CONFIG_FILE = "/home/user/cfg.json"
    category2 = ReadonlyConfigCategory(path, False)
    assert category2.CHART_POLICIES_CONFIG_FILE == "/home/user/cfg.json"


def test_config_manager():
    folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'json')
    ConfigureManager(folder)
