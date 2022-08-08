from dataclasses import dataclass
from enum import Enum, auto
from typing import List, TYPE_CHECKING

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from .scenario import StockScenario


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
        self.price_history[0][0] = scenario.stock_price_start
        self.volume_history = np.zeros((self.scenario.periods, self.scenario.period_ticks))

    def get_latest_price(self, period: int, tick: int):
        if period == 0 and tick == 0:
            price = self.price_history[period][tick]
        elif period > 0 and tick == 0:
            price = self.price_history[period - 1][self.scenario.period_ticks - 1]
        else:
            price = self.price_history[period][tick - 1]
        return price

    def process_order(self, period: int, tick: int, order: 'Order'):
        if order.type == OrderType.BID:
            transaction = self.process_bid_order(period, tick, order)
        else:
            transaction = self.process_ask_order(period, tick, order)
        return transaction

    def process_bid_order(self, period: int, tick: int, bid_order: 'Order'):
        transaction = None
        if len(self.ask_orders) > 0:
            best_ask_order = self.ask_orders[0]
            if best_ask_order.price <= bid_order.price:
                transaction = self.match_orders(period, tick, bid_order, best_ask_order)
            else:
                self.insert_bid_order(bid_order)
        else:
            self.insert_bid_order(bid_order)
        return transaction

    def process_ask_order(self, period: int, tick: int, ask_order: 'Order'):
        transaction = None
        if len(self.bid_orders) > 0:
            best_bid_order = self.bid_orders[0]
            if best_bid_order.price >= ask_order.price:
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
        print(f'coming_bid_order = {coming_order}')
        if len(self.bid_orders) > 0:
            for index, order in enumerate(self.bid_orders):
                if order.price <= coming_order.price:
                    self.bid_orders.insert(index, coming_order)
                    break
        else:
            self.bid_orders.append(coming_order)

    def insert_ask_order(self, coming_order: 'Order'):
        print(f'coming_ask_order = {coming_order}')
        if len(self.ask_orders) > 0:
            for index, order in enumerate(self.ask_orders):
                if order.price >= coming_order.price:
                    self.ask_orders.insert(index, coming_order)
                    break
        else:
            self.ask_orders.append(coming_order)

    def clear_orders(self):
        self.bid_orders = []
        self.ask_orders = []

    def get_price_volume_history_df(self):
        price_volume_history = []
        for period in range(0, self.scenario.periods):
            prices = self.price_history[period]
            volumes = self.volume_history[period]
            price_volume_history.append({
                "period": period,
                "open": prices[0],
                "high": np.max(prices),
                "low": np.min(prices),
                "mean": np.mean(prices),
                "close": prices[self.scenario.period_ticks - 1],
                "volume": np.sum(volumes)
            })
        df = pd.DataFrame(price_volume_history)
        return df

    def get_transaction_history_df(self):
        transaction_history = [transaction.__dict__ for transaction in self.transactions]
        df = pd.DataFrame(transaction_history)
        return df
