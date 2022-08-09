from dataclasses import dataclass
from enum import Enum, auto
from typing import List, TYPE_CHECKING, Union

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from .scenario import StockScenario
    from Melodie import AgentList
    from .agent import StockAgent


class OrderType(Enum):
    BID = auto()
    ASK = auto()


@dataclass
class Order:
    agent_id: int
    type: 'OrderType' = None
    price: float = None
    volume: int = None


@dataclass
class Transaction:
    period: int
    tick: int
    buyer_id: int = None
    seller_id: int = None
    price: float = None
    volume: int = None


class OrderBook:

    def __init__(self, scenario: 'StockScenario'):
        self.scenario = scenario
        self.bid_orders: List['Order'] = []
        self.ask_orders: List['Order'] = []
        self.transactions: List['Transaction'] = []
        self.price_history = np.zeros((self.scenario.periods, self.scenario.period_ticks))
        self.volume_history = np.zeros((self.scenario.periods, self.scenario.period_ticks))

    def clear_orders(self):
        self.bid_orders = []
        self.ask_orders = []

    def get_current_price(self, period: int, tick: int):
        if period == 0 and tick == 0:
            price = self.scenario.stock_price_start
        elif period > 0 and tick == 0:
            price = self.price_history[period - 1][self.scenario.period_ticks - 1]
        else:
            price = self.price_history[period][tick - 1]
        return price

    def get_period_close_price(self, period: int):
        return self.price_history[period, self.scenario.period_ticks - 1]

    def get_memorized_close_price_series(self, period: int, memory_length: int):
        close_price_series = self.price_history[:, self.scenario.period_ticks - 1]
        if period == 0:
            price_series = np.array([close_price_series[0]])
        elif 0 < period < memory_length:
            price_series = close_price_series[0:period + 1]
        else:
            price_series = close_price_series[period - memory_length:period + 1]
        return price_series

    def process_order(self, order: 'Order', period: int, tick: int):
        if order.type == OrderType.BID:
            transaction = self.process_bid_order(period, tick, order)
        else:
            transaction = self.process_ask_order(period, tick, order)
        return transaction

    def process_bid_order(self, period: int, tick: int, bid_order: 'Order'):
        transaction = None
        if len(self.ask_orders) > 0:
            if self.ask_orders[0].price <= bid_order.price:
                best_ask_order = self.ask_orders.pop(0)
                transaction = self.match_orders(period, tick, bid_order, best_ask_order)
            else:
                self.insert_bid_order(bid_order)
        else:
            self.insert_bid_order(bid_order)
        return transaction

    def process_ask_order(self, period: int, tick: int, ask_order: 'Order'):
        transaction = None
        if len(self.bid_orders) > 0:
            if self.bid_orders[0].price >= ask_order.price:
                best_bid_order = self.bid_orders.pop(0)
                transaction = self.match_orders(period, tick, best_bid_order, ask_order)
            else:
                self.insert_ask_order(ask_order)
        else:
            self.insert_ask_order(ask_order)
        return transaction

    def match_orders(self, period: int, tick: int, bid_order: 'Order', ask_order: 'Order'):
        transaction = Transaction(period, tick)
        transaction.buyer_id = bid_order.agent_id
        transaction.seller_id = ask_order.agent_id
        transaction.price = 0.5 * (bid_order.price + ask_order.price)
        transaction.volume = bid_order.volume
        self.transactions.append(transaction)
        return transaction

    def insert_bid_order(self, coming_order: 'Order'):
        if len(self.bid_orders) > 0:
            for index, order in enumerate(self.bid_orders):
                if order.price <= coming_order.price:
                    self.bid_orders.insert(index, coming_order)
                    break
        else:
            self.bid_orders.append(coming_order)

    def insert_ask_order(self, coming_order: 'Order'):
        if len(self.ask_orders) > 0:
            for index, order in enumerate(self.ask_orders):
                if order.price >= coming_order.price:
                    self.ask_orders.insert(index, coming_order)
                    break
        else:
            self.ask_orders.append(coming_order)

    def process_transaction(self, agents: 'AgentList[StockAgent]',
                            transaction: Union['None', 'Transaction'],
                            period: int, tick: int):
        if transaction is not None:
            buyer = agents.get_agent(transaction.buyer_id)
            buyer.cash_account -= transaction.price * transaction.volume
            buyer.stock_account += transaction.volume
            seller = agents.get_agent(transaction.seller_id)
            seller.cash_account += transaction.price * transaction.volume
            seller.stock_account -= transaction.volume
            self.price_history[period][tick] = transaction.price
            self.volume_history[period][tick] = transaction.volume
        else:
            self.price_history[period][tick] = self.get_current_price(period, tick)
            self.volume_history[period][tick] = 0

    def get_transaction_history_df(self):
        transaction_history = [transaction.__dict__ for transaction in self.transactions]
        df = pd.DataFrame(transaction_history)
        return df

    def get_best_bid_price(self):
        price = None
        if len(self.bid_orders) > 0:
            price = self.bid_orders[0].price
        return price

    def get_best_ask_price(self):
        price = None
        if len(self.ask_orders) > 0:
            price = self.ask_orders[0].price
        return price
