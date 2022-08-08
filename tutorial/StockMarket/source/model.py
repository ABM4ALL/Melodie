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
        self.environment: "StockEnvironment" = self.create_environment(StockEnvironment)
        self.data_collector: "StockDataCollector" = self.create_data_collector(StockDataCollector)

    def setup(self):
        self.agents.setup_agents(self.scenario.agent_num,
                                 self.scenario.get_dataframe(data_info.agent_params))

    def run(self):
        for period in self.iterator(self.scenario.periods):
            print(f'period = {period}')
            self.environment.update_forecasts(period)
            for tick in range(0, self.scenario.period_ticks):
                self.environment.stock_trading(self.agents, period, tick)
            self.environment.order_book.clear_orders()
            self.environment.calculate_forecast_rule_deviation(period)
            self.environment.agents_update_forecast_rule(self.agents)
            self.environment.agents_update_wealth(self.agents, period)
            self.data_collector.collect(period)
        self.data_collector.save()
        self.data_collector.save_order_book(self.environment.order_book)
