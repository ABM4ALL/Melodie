# -*- coding:utf-8 -*-
# @Time: 2021/11/16 9:25
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: configure_manager.py
import os.path
from typing import Optional

from .file_manager import JSONManager

COMPULSORY_CONFIGS_DIR = os.path.join(os.path.dirname(__file__), "compulsory_configs")


class ConfigureCategory():
    def __init__(self, file_path: str, readonly: bool = True):
        self.__dict__['_initalized'] = False
        self._file = file_path
        self._readonly = readonly
        self.setup()
        self.load()
        self._initalized = True

    def setup(self):
        """
        Setup function, must be inherited.
        :return:
        """
        pass

    def load(self):
        """
        Load configures from json file
        :return:
        """
        if not os.path.exists(self._file):
            d = self.to_dict()
            err = JSONManager.to_file(d, self._file)
            if err is not None:
                raise Exception(err)

        config, err = JSONManager.from_file(self._file, dict)
        if err is not None:
            raise Exception(err)

        for k, v in self.__dict__.items():
            if k.startswith('_'):
                continue
            if k in config:
                self.__dict__[k] = config[k]
            else:
                raise AttributeError(f"Configure file {self._file} does not define '{k}'")

    def to_dict(self):
        """
        Convert to dict
        :return:
        """
        d = {}
        for k, v in self.__dict__.items():
            if not k.startswith("_"):
                d[k] = v
        return d

    def save(self):
        """
        Save configures to json file.
        :return:
        """
        if self._readonly:
            raise PermissionError("This config category is readonly")
        err = JSONManager.to_file(self.to_dict(), self._file)
        if err is not None:
            raise Exception(err)

    def __setattr__(self, key, value):
        if not self._initalized:
            super(ConfigureCategory, self).__setattr__(key, value)
        else:
            assert key in self.__dict__, AttributeError(f"Configure category has no property '{key}'")
            self.__dict__[key] = value
            self.save()

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.to_dict()}>"


class BasicConfig(ConfigureCategory):
    def setup(self):
        self.PORT = 8089
        self.WS_SOCKET = 8765
        self.CHART_STYLE_CONFIG_FILE = ""
        self.CHART_POLICIES_FILE = os.path.join(COMPULSORY_CONFIGS_DIR, "chart_policies.json")


class ConfigureManager:
    def __init__(self, conf_folder: str):
        if not os.path.exists(conf_folder):
            os.mkdir(conf_folder)
        elif os.path.isfile(conf_folder):
            raise FileExistsError(f"Config folder '{conf_folder}' is a file, not a folder")
        self.basic_config = BasicConfig(os.path.join(conf_folder, 'basic_config.json'), False)
        self.basic_config.CHART_STYLE_CONFIG_FILE = os.path.join(conf_folder, 'chart_options.json')


_config_manager: Optional[ConfigureManager] = None


def init_config_manager(conf_folder: str):
    """
    initialize the config manager
    :param conf_folder:
    :return:
    """
    global _config_manager
    _config_manager = ConfigureManager(conf_folder)


def get_config_manager():
    """
    Get the config manager instance.
    :return:
    """
    global _config_manager
    assert _config_manager is not None
    return _config_manager
