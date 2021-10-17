# -*- coding:utf-8 -*-
# @Time: {{cookiecutter.created_at}}
# @Author: {{cookiecutter.author}}
# @Email: {{cookiecutter.email}}

from Melodie import Model


class _ALIAS_Model(Model):
    def setup(self):
        pass

    def step(self):
        self.environment.step()