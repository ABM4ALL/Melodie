# -*- coding: utf-8 -*-
__author__ = 'Songmin'

from Melodie import Model
from .scenario import AspirationScenario
from .agent import AspirationAgent
from .environment import AspirationEnvironment


class AspirationModel(Model):
    environment: AspirationEnvironment # 有点儿奇怪，为什么没有self也可以hint type？
    scenario: AspirationScenario

    def setup(self):
        self.agent_list = self.create_agent_container(AspirationAgent,
                                                      self.scenario.agent_num,
                                                      self.scenario.get_registered_dataframe('agent_params'))

    def run(self):
        for t in range(0, self.scenario.periods):
            self.environment.market_process(self.agent_list)
            self.environment.aspiration_update_process(self.agent_list)
            self.environment.technology_search_process(self.agent_list)
            self.environment.calculate_environment_result(self.agent_list)
            self.data_collector.collect(t)
        self.data_collector.save()
