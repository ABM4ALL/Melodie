# -*- coding:utf-8 -*-
# @Time: {{cookiecutter.created_at}}
# @Author: {{cookiecutter.author}}
# @Email: {{cookiecutter.email}}

from Melodie import Scenario


class _ALIAS_Scenario(Scenario):
    def setup(self):
        self.agent_num = 100
        self.number_of_run = 1
        self.periods = 100

        self.agent_a_min = 0
        self.agent_a_max = 100