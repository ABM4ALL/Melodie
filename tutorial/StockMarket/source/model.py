from typing import TYPE_CHECKING

from Melodie import Model
from tutorial.CovidContagion.source import data_info
from .agent import StockAgent
from .data_collector import StockDataCollector
from .environment import StockEnvironment
from .scenario import StockScenario

if TYPE_CHECKING:
    from Melodie import AgentList


class StockModel(Model):
    scenario: StockScenario

    def create(self):
        self.agents: "AgentList[StockAgent]" = self.create_agent_list(StockAgent)
        self.environment = self.create_environment(StockEnvironment)
        self.data_collector = self.create_data_collector(StockDataCollector)

    def setup(self):
        self.agents.setup_agents(self.scenario.agent_num,
                                 self.scenario.get_dataframe(data_info.agent_params))

    def run(self):
        for t in self.iterator(self.scenario.periods):
            self.data_collector.collect(t)
        self.data_collector.save()
