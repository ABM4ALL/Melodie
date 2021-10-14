# -*- coding: utf-8 -*-
__author__ = 'Songmin'

from Melodie import Model


class GiniModel(Model):

    def run(self):
        simulation_periods = self.scenario.periods
        agent_manager = self.agent_manager
        dc = self.data_collector

        for t in range(0, simulation_periods):
            print("ID_Scenario = " + str(self.scenario.id) + ", period = " + str(t))

            self.environment.go_money_produce(agent_manager)
            self.environment.go_money_transfer(agent_manager)
            self.environment.calc_wealth_and_gini(agent_manager)
            dc.collect(t)
        dc.save()

