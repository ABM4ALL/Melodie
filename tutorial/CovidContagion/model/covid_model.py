from typing import TYPE_CHECKING
from Melodie import Model
from .agent import CovidAgent
from .environment import CovidEnvironment
from .data_collector import CovidDataCollector
from .scenario import CovidScenario
from .grid import CovidSpot, CovidGrid
from .network import CovidEdge, CovidNetwork
from tutorial.CovidContagion.model import dataframe_info as df_info

if TYPE_CHECKING:
    from Melodie import AgentList


class CovidModel(Model):
    scenario: CovidScenario

    def setup(self):  # create和setup两个概念也需要统一
        self.agents: "AgentList[CovidAgent]" = self.create_agent_list(
            CovidAgent,
            self.scenario.agent_num,
            self.scenario.get_dataframe(df_info.agent_params),
        )

        self.grid = self.create_grid(
            CovidGrid,
            CovidSpot,
            self.scenario.grid_x_size,
            self.scenario.grid_y_size,
            multi=True
        )
        self.grid.add_agent_container(0, self.agents, "direct")  # direct这个参数名不太清楚

        # grid的四边相连？模拟看到了x = -1

        self.environment = self.create_environment(CovidEnvironment)
        self.data_collector = self.create_data_collector(CovidDataCollector)

    def run(self):
        self.scenario.setup_age_group_params()
        for t in self.iterator(
                self.scenario.periods
        ):  # 可以把scenario.periods传入self.iterator。
            for hour in range(0, self.scenario.period_hours):
                self.environment.agents_move(self.agents)
                self.environment.agents_infection(self.agents, self.grid)
            self.environment.agents_health_state_transition(self.agents)
            self.environment.calc_agents_health_state(self.agents)
            self.data_collector.collect(t)
        self.data_collector.save()
