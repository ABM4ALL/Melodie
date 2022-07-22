# -*- coding: utf-8 -*-
__author__ = "Songmin"

import os
import time

import psutil

from Melodie import Model, AgentList, Grid, Spot
from Melodie.boost import vectorize
from .environment import CovidEnvironment, CovidAgent
from .data_collector import CovidDataCollector
from .scenario import CovidScenario


class CovidModel(Model):
    scenario: CovidScenario

    def setup(self):
        self.agent_list: AgentList[CovidAgent] = self.create_agent_container(
            CovidAgent,
            self.scenario.agent_num,
            self.scenario.get_registered_dataframe("agent_params"),
            "list",
        )

        with self.define_basic_components():
            self.environment = CovidEnvironment()
            self.data_collector = CovidDataCollector()

            self.grid = Grid(
                Spot,
                self.scenario.grid_x_size,
                self.scenario.grid_y_size,
                caching=True,
                multi=True,
            )
            self.grid.add_agent_container(0, self.agent_list, "direct")

    def run(self):
        for t in self.routine():
            self.environment.agents_move(self.agent_list, self.grid)
            self.environment.agents_infection(self.agent_list, self.grid)
            self.environment.calculate_accumulated_infection(self.agent_list)
        #     self.data_collector.collect(t)
        # self.data_collector.save()
