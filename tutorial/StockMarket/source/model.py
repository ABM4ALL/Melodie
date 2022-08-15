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
        self.data_collector: "StockDataCollector" = self.create_data_collector(
            StockDataCollector
        )

    def setup(self):
        self.agents.setup_agents(
            self.scenario.agent_num, self.scenario.get_dataframe(data_info.agent_params)
        )

    def run(self):
        for period in self.iterator(self.scenario.period_num):
            self.environment.order_book.clear_orders()
            for tick in range(0, self.scenario.period_ticks):
                agent = self.agents.random_sample(1)[0]
                current_price = self.environment.order_book.get_current_price(
                    period, tick
                )
                order = agent.create_order(current_price)
                transaction = self.environment.order_book.process_order(
                    order, period, tick
                )
                self.environment.order_book.process_transaction(
                    self.agents, transaction, period, tick
                )
            self.environment.record_period_trading_info(period)
            self.environment.agents_update_wealth(self.agents, period)
            self.environment.agents_update_forecast(self.agents, period)
            self.data_collector.collect(period)
        self.data_collector.save()
        self.data_collector.save_transaction_history(self.environment.order_book)
        self.data_collector.save_price_volume_history(self.environment.order_book)
