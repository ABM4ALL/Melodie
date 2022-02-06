# -*- coding: utf-8 -*-
__author__ = 'Songmin'

from Melodie import Model, AgentList
from .agent import AspirationAgent
from .environment import AspirationEnvironment
from .data_collector import AspirationDataCollector


class AspirationModel(Model):

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
        # account_sum = 0
        # for agent in self.agent_list:
        #     agent.account = agent.strategy_param_1 + agent.strategy_param_2 + agent.strategy_param_3
        #     account_sum += agent.account
        # self.environment.average_technology = account_sum / len(self.agent_list)
        # return
        for t in range(0, self.scenario.periods):
            self.environment.market_process(self.agent_list)
            self.environment.aspiration_update_process(self.agent_list)
            self.environment.technology_search_process(self.agent_list)
            self.environment.calculate_environment_result(self.agent_list)
            # self.data_collector.collect(t)
        # self.data_collector.save()
