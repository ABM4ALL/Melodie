from typing import TYPE_CHECKING, Union

import numpy as np

from Melodie import Environment
from .forecaster import Forecaster
from .order_book import OrderBook

if TYPE_CHECKING:
    from Melodie import AgentList
    from .agent import StockAgent
    from .scenario import StockScenario
    from .order_book import Transaction


class StockEnvironment(Environment):
    scenario: 'StockScenario'

    def setup(self):
        self.order_book = OrderBook(self.scenario)
        self.forecaster = Forecaster(self.scenario)
        self.fundamentalist_forecasts = np.zeros((self.scenario.periods, ))
        self.chartist_forecasts = np.zeros((self.scenario.periods, ))
        self.fundamentalist_deviation = 0
        self.chartist_deviation = 0

    @staticmethod
    def get_earliest_memory_period(memory_length: int, period: int):
        if period >= memory_length:
            earliest_memory_period = period - memory_length
        else:
            earliest_memory_period = 0
        return earliest_memory_period

    def update_forecasts(self, period: int):
        self.update_fundamentalist_forecast(period)
        self.update_chartist_forecast(period)

    def update_fundamentalist_forecast(self, period: int):




        forecast = self.forecaster.update_fundamentalist_forecast()
        self.fundamentalist_forecasts[period] = forecast

    def update_chartist_forecast(self, period: int):
        price_history = self.order_book.price_history
        memory_length = self.scenario.chartist_memory_length
        period_ticks = self.scenario.period_ticks
        start_period = self.get_earliest_memory_period(memory_length, period)
        price_series = price_history[start_period:period, period_ticks - 1]
        forecast = self.forecaster.update_chartist_forecast(price_series)
        self.chartist_forecasts[period] = forecast

    def stock_trading(self, agents: 'AgentList[StockAgent]', period: int, tick: int):
        agent: 'StockAgent' = agents.random_sample(1)[0]
        latest_price = self.order_book.get_latest_price(period, tick)
        order = agent.create_order(self.forecaster, latest_price)
        transaction: 'Transaction' = self.order_book.process_order(period, tick, order)
        self.process_transaction(agents, period, tick, transaction)

    def process_transaction(self, agents: 'AgentList[StockAgent]',
                            period: int, tick: int, transaction: Union['None', 'Transaction']):
        if transaction is not None:
            buyer = agents[transaction.buyer_id]
            buyer.cash_account -= transaction.price * transaction.volume
            buyer.stock_account += transaction.volume
            seller = agents[transaction.seller_id]
            seller.cash_account += transaction.price * transaction.volume
            seller.stock_account -= transaction.volume
            self.order_book.price_history[period][tick] = transaction.price
            self.order_book.volume_history[period][tick] = transaction.volume
        else:
            self.order_book.price_history[period][tick] = self.order_book.get_latest_price(period, tick)
            self.order_book.volume_history[period][tick] = 0

    def calculate_forecast_rule_deviation(self, period: int):
        memory_length = self.scenario.forecast_rule_evaluation_memory
        period_ticks = self.scenario.period_ticks
        start_period = self.get_earliest_memory_period(memory_length, period)
        fundamentalist_forecasts = self.fundamentalist_forecasts[start_period:period]
        chartist_forecasts = self.chartist_forecasts[start_period:period]
        price_series = self.order_book.price_history[start_period:period, period_ticks - 1]
        self.fundamentalist_deviation = self.calculate_deviation(fundamentalist_forecasts, price_series)
        self.chartist_deviation = self.calculate_deviation(chartist_forecasts, price_series)

    @staticmethod
    def calculate_deviation(forecast_series: np.ndarray, price_series: np.ndarray):
        deviation = np.sum((forecast_series - price_series) ** 2)
        return deviation

    def agents_update_forecast_rule(self, agents: 'AgentList[StockAgent]'):
        for agent in agents:
            agent.update_forecast_rule(self.fundamentalist_deviation, self.chartist_deviation)














