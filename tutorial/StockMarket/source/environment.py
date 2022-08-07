from typing import TYPE_CHECKING

from Melodie import Environment
from .scenario import StockScenario
from .order_book import OrderBook
from .forecaster import Forecaster

if TYPE_CHECKING:
    pass


class StockEnvironment(Environment):
    scenario: StockScenario

    def setup(self):
        self.order_book = OrderBook()
        self.forecaster = Forecaster(self.scenario.chartist_memory_length,
                                     self.scenario.fundamentalist_price_benchmark)



