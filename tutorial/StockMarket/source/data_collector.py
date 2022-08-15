from typing import TYPE_CHECKING

import pandas as pd

from Melodie import DataCollector

if TYPE_CHECKING:
    from .order_book import OrderBook
    from .scenario import StockScenario



class StockDataCollector(DataCollector):
    scenario: "StockScenario"

    def setup(self):
        self.add_agent_property("agents", "fundamentalist_weight")
        self.add_agent_property("agents", "fundamentalist_forecast")
        self.add_agent_property("agents", "chartist_forecast")
        self.add_agent_property("agents", "forecast")
        self.add_agent_property("agents", "stock_account")
        self.add_agent_property("agents", "cash_account")
        self.add_agent_property("agents", "wealth_period")
        self.add_environment_property("open")
        self.add_environment_property("high")
        self.add_environment_property("low")
        self.add_environment_property("mean")
        self.add_environment_property("close")
        self.add_environment_property("volume")

    def save_transaction_history(self, order_book: "OrderBook"):
        transaction_history_df = order_book.get_transaction_history_df()
        self.db.write_dataframe("transaction_history", transaction_history_df)

    def save_price_volume_history(self, order_book: "OrderBook"):
        price_volume_history = []
        for period in range(0, self.scenario.period_num):
            for tick in range(0, self.scenario.period_ticks):
                price_volume_history.append({
                    "period": period,
                    "tick": tick,
                    "price": order_book.price_history[period][tick],
                    "volume": order_book.volume_history[period][tick]
                })
        self.db.write_dataframe("price_volume_history", pd.DataFrame(price_volume_history))
