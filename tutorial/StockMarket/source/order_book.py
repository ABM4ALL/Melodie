from dataclasses import dataclass
from enum import Enum, auto
from typing import List


class OrderType(Enum):
    BID = auto()
    ASK = auto()


@dataclass
class Order:
    type: 'OrderType'
    price: int
    volume: int


@dataclass
class Record:
    period: int
    tick: int
    buyer_id: int = None
    seller_id: int = None
    price: int = None
    volume: int = None


class OrderBook:

    def __init__(self):
        self.orders: List[Order] = []
        self.records: List[Record] = []

    def clear_orders(self):
        self.orders = []

    def match(self):
        # trading_record = Record(period, tick)
        # self.records.append(trading_record)
        ...

