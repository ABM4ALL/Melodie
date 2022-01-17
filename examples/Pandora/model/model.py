# -*- coding: utf-8 -*-
__author__ = 'Songmin'

from Melodie import Model, AgentList, Grid, Spot
from .agent import PandoraAgent
from .environment import PandoraEnvironment
from .data_collector import PandoraDataCollector
from .scenario import PandoraScenario


class PandoraModel(Model):
    scenario: PandoraScenario

    def setup(self):
        self.agent_list: AgentList[PandoraAgent] = self.create_agent_container(PandoraAgent,
                                                                             self.scenario.agent_num,
                                                                             self.scenario.get_registered_dataframe(
                                                                                 'agent_params'))

        with self.define_basic_components():
            self.environment = PandoraEnvironment()
            self.data_collector = PandoraDataCollector()

            self.grid = Grid(Spot, self.scenario.grid_x_size, self.scenario.grid_y_size, caching=False)
            self.grid.add_category('agent_list')

            for agent in self.agent_list:
                self.grid.add_agent(agent.id, "agent_list", agent.x_pos, agent.y_pos)

            # self.grid.move_agent(0, "agent_list", 9, 0)
            # self.grid.get_agent_pos(0, 'agent_list')  # 获取0号agent的位置。

    def run(self):
        for t in range(0, self.scenario.periods):
            self.environment.agents_move(self.agent_list, self.grid)
            self.environment.agents_infection(self.agent_list, self.grid)
            self.data_collector.collect(t)
        self.data_collector.save()
