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

    def get_close_price_series_in_memory(self, period: int, memory_length: int):
        if period == 0:
            price_series = np.array([self.order_book.price_history[0][0]])
        elif 0 < period < memory_length:
            price_series = self.order_book.price_history[0:period, self.scenario.period_ticks - 1]
        else:
            price_series = self.order_book.price_history[period - memory_length:period, self.scenario.period_ticks - 1]
        return price_series

    @staticmethod
    def get_forecast_series_in_memory(forecasts: np.ndarray, period: int, memory_length: int):
        if period == 0:
            forecast_series = np.array([forecasts[0]])
        elif 0 < period < memory_length:
            forecast_series = forecasts[0:period + 1]
        else:
            forecast_series = forecasts[period - memory_length:period + 1]
        return forecast_series

    def update_forecasts(self, period: int):
        self.update_fundamentalist_forecast(period)
        self.update_chartist_forecast(period)

    def update_fundamentalist_forecast(self, period: int):
        forecast = self.forecaster.update_fundamentalist_forecast()
        self.fundamentalist_forecasts[period] = forecast

    def update_chartist_forecast(self, period: int):
        price_series = self.get_close_price_series_in_memory(period, self.scenario.chartist_memory_length)
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
        memory_length = self.scenario.forecast_rule_evaluation_memory_length
        fundamentalist_forecasts = self.get_forecast_series_in_memory(self.fundamentalist_forecasts, period, memory_length)
        chartist_forecasts = self.get_forecast_series_in_memory(self.chartist_forecasts, period, memory_length)
        price_series = self.get_close_price_series_in_memory(period + 1, memory_length + 1)
        self.fundamentalist_deviation = self.calculate_deviation(fundamentalist_forecasts, price_series)
        self.chartist_deviation = self.calculate_deviation(chartist_forecasts, price_series)

    @staticmethod
    def calculate_deviation(forecast_series: np.ndarray, price_series: np.ndarray):
        deviation = np.sum((forecast_series - price_series) ** 2)
        return deviation

    def agents_update_forecast_rule(self, agents: 'AgentList[StockAgent]'):
        for agent in agents:
            agent.update_forecast_rule(self.fundamentalist_deviation, self.chartist_deviation)














