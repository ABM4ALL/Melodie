# -*- coding: utf-8 -*-
__author__ = 'Songmin'

from Melodie import Model,current_scenario
from .agent import GINIAgent
from .data_collector import GiniDataCollector
from .environment import GiniEnvironment


class GiniModel(Model):
    def setup(self):
        self.agent_class = GINIAgent
        self.data_collector_class = GiniDataCollector
        self.environment_class = GiniEnvironment

    def run(self):

        agent_manager = self.agent_manager
        dc = self.data_collector

        for t in range(0, current_scenario().periods):
            self.environment.go_money_produce(agent_manager)
            self.environment.go_money_transfer(agent_manager)
            self.environment.calc_wealth_and_gini(agent_manager)
            dc.collect(t)
        dc.save()
