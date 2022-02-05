# -*- coding: utf-8 -*-
__author__ = 'Songmin'

from Melodie import Model, AgentList
from .scenario import AspirationScenario
from .agent import AspirationAgent
from .environment import AspirationEnvironment
from .data_collector import AspirationDataCollector


class AspirationModel(Model):
    scenario: AspirationScenario
    
    def setup(self):

        self.agent_list: AgentList[AspirationAgent] = self.create_agent_container(
            AspirationAgent,
            self.scenario.agent_num,
            self.scenario.get_registered_dataframe('agent_params')
        )

        with self.define_basic_components():
            self.environment = AspirationEnvironment()
            self.data_collector = AspirationDataCollector()

    def run(self):
        for t in range(0, self.scenario.periods):
            self.environment.market_process(self.agent_list)
            self.environment.aspiration_update_process(self.agent_list)
            self.environment.technology_search_process(self.agent_list)
            self.environment.calculate_average_technology(self.agent_list)
            self.environment.calculate_technology_search_strategy_share(self.agent_list)
        #     self.data_collector.collect(t)
        # self.data_collector.save()
