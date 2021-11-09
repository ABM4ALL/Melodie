# -*- coding: utf-8 -*-
__author__ = 'Songmin'

from Melodie import DataCollector


class GiniDataCollector(DataCollector):
    def setup(self):
        self.add_agent_property("agent_list", 'account')
        self.add_environment_property('trade_num')
        self.add_environment_property('win_prob')
        self.add_environment_property('total_wealth')
        self.add_environment_property('gini')
