# -*- coding: utf-8 -*-
__author__ = 'Songmin'

from Melodie import Model, AgentList
from .agent import CovidAgent
from .environment import CovidEnvironment
from .data_collector import CovidDataCollector


class CovidModel(Model):

    def setup(self):

        self.agent_list: AgentList[CovidAgent] = self.create_agent_container(CovidAgent,
                                                                             self.scenario.agent_num,
                                                                             self.scenario.get_registered_dataframe('agent_params'))

        with self.define_basic_components():
            self.environment = CovidEnvironment()
            self.data_collector = CovidDataCollector()

    def run(self):
        for t in range(0, self.scenario.periods):
            self.environment.agents_move(self.agent_list)
            self.environment.agents_infection(self.agent_list)
            self.data_collector.collect(t)
        self.data_collector.save()
