# -*- coding: utf-8 -*-
__author__ = 'Songmin'

from Melodie import Model, AgentList
from .scenario import TechnologySearchScenario
from .agent import TechnologySearchAgent
from .environment import TechnologySearchEnvironment
from .data_collector import TechnologySearchDataCollector


class TechnologySearchModel(Model):
    scenario: TechnologySearchScenario

    def setup(self):
        self.agent_list: AgentList[TechnologySearchAgent] = self.create_agent_container(
            TechnologySearchAgent,
            self.scenario.agent_num,
            self.scenario.get_registered_dataframe('agent_params')
        )

        with self.define_basic_components():
            self.environment = TechnologySearchEnvironment()
            self.data_collector = TechnologySearchDataCollector()

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
        print(self.agent_list.get_agent(0).account,
              (self.agent_list.get_agent(0).exploration_count,
               self.agent_list.get_agent(0).exploitation_count,
               self.agent_list.get_agent(0).imitation_count,),
              (
                  self.agent_list.get_agent(0).prob_exploration,
                  self.agent_list.get_agent(0).prob_exploitation,
              ),
              self.agent_list.get_agent(0).strategy_param_1,
              self.agent_list.get_agent(0).strategy_param_2, self.agent_list.get_agent(0).strategy_param_3)
        # print(
        # print(self).agent_list.get_agent(0).exploitation_count)
        #     self.data_collector.collect(t)
        # self.data_collector.save()
