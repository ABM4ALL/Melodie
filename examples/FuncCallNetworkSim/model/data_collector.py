# -*- coding: utf-8 -*-
__author__ = 'Songmin'

from Melodie import DataCollector


class FuncDataCollector(DataCollector):
    def setup(self):
        self.add_agent_property('status')
