# -*- coding: utf-8 -*-
__author__ = 'Songmin'

from Melodie import Model, AgentList
from .scenario import OptimalConsumptionScenario
from .agent import OptimalConsumptionAgent
from .environment import OptimalConsumptionEnvironment
from .data_collector import OptimalConsumptionDataCollector


class OptimalConsumptionModel(Model):
    scenario: OptimalConsumptionScenario
    
    def setup(self):

        self.agent_list: AgentList[OptimalConsumptionAgent] = self.create_agent_container(
            OptimalConsumptionAgent,
            self.scenario.agent_num,
            self.scenario.get_registered_dataframe('agent_params')
        )

        with self.define_basic_components():
            self.environment = OptimalConsumptionEnvironment()
            self.data_collector = OptimalConsumptionDataCollector()

    def run(self):
        self.environment.agent_post_setup(self.agent_list)
        for t in range(0, self.scenario.periods):
            # print(f'Period = {t}')
            self.environment.market_process(self.agent_list)
            self.environment.aspiration_update_process(self.agent_list)
            self.environment.technology_search_process(self.agent_list)
            self.environment.calculate_average_technology(self.agent_list)
            self.environment.calculate_account_total(self.agent_list)
            self.environment.calculate_technology_search_strategy_share(self.agent_list)
        #     self.data_collector.collect(t)
        # self.data_collector.save()

