# -*- coding: utf-8 -*-
__author__ = 'Songmin'

from Melodie import Model, AgentList
from .scenario import RPSScenario
from .agent import RPSAgent
from .environment import RPSEnvironment
from .data_collector import RPSDataCollector


class RPSModel(Model):
    scenario: RPSScenario
    
    def setup(self):

        self.agent_list: AgentList[RPSAgent] = self.create_agent_container(
            RPSAgent,
            self.scenario.agent_num,
            self.scenario.get_registered_dataframe('agent_params')
        )

        with self.define_basic_components():
            self.environment = RPSEnvironment()
            self.data_collector = RPSDataCollector()

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

