# -*- coding: utf-8 -*-
__author__ = 'Songmin'

from Melodie import Model
from .agent import GINIAgent
from .data_collector import GiniDataCollector
from .environment import GiniEnvironment


class GiniModel(Model):

    # 让用户自己setup agent_list -->
    # self.wolf_list = self.setup_agent_list(scenario.get_registered_table("wolf_params")[id_scenario == scenario.id])
    # self.sheep_list = self.setup_agent_list(scenario.get_registered_table("sheep_params"))

    def run(self):

        for t in range(0, self.scenario.periods):
            self.environment.go_money_produce(self.agent_list)
            self.environment.go_money_transfer(self.agent_list)
            self.environment.calc_wealth_and_gini(self.agent_list)
            self.data_collector.collect(t)
        self.data_collector.save()

