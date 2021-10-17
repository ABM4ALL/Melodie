# -*- coding:utf-8 -*-
# @Time: {{cookiecutter.created_at}}
# @Author: {{cookiecutter.author}}
# @Email: {{cookiecutter.email}}

from Melodie import DataCollector


class _ALIAS_DataCollector(DataCollector):
    def setup(self):
        self.add_agent_property('a')
