from typing import TYPE_CHECKING

from Melodie import DataCollector

if TYPE_CHECKING:
    from .order_book import OrderBook


class StockDataCollector(DataCollector):
    def setup(self):
        self.add_agent_property("agents", "forecast_rule_id")
        self.add_agent_property("agents", "stock_account")
        self.add_agent_property("agents", "cash_account")
        self.add_agent_property("agents", "wealth")
        self.add_environment_property("fundamentalist_deviation")
        self.add_environment_property("chartist_deviation")

    def save_order_book(self, order_book: "OrderBook"):
        price_volume_history_df = order_book.get_price_volume_history_df()
        transaction_history_df = order_book.get_transaction_history_df()
        self.db.write_dataframe()
