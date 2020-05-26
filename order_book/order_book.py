import bisect
import json
from typing import List


class OrderEntry:
    def __init__(self, order_json):
        self.type_: str = order_json['type']

        order = order_json['order']
        self.direction: str = order['direction']
        self.id: int = order['id']
        self.price: int = order['price']
        self.quantity: int = order['quantity']
        self.direction: str = order['direction']
        self.peak: int = order.get('peak', None)

    def is_iceberg(self):
        return self.type_ == 'Iceberg'

    def is_buy_order(self):
        return self.direction == 'Buy'

    def to_json(self):
        return {
            'id': self.id,
            'price': self.price,
            'quantity': self.quantity,
        }

    def __repr__(self):
        return json.dumps(self.__dict__)

    def __lt__(self, other):
        if self.price == other.price:
            # Assuming ID order is the same as appearance order
            return self.id < other.id
        return self.price < other.price


class OrderCollection:
    def __init__(self):
        self.orders: List[OrderEntry] = []

    def to_json(self):
        return [o.to_json() for o in self.orders]

    def insert(self, order: OrderEntry):
        bisect.insort_right(self.orders, order)

    def __repr__(self):
        return json.dumps(self.__dict__)


class OrderBook:
    def __init__(self):
        self.buyOrders: OrderCollection = OrderCollection()
        self.sellOrders: OrderCollection = OrderCollection()

    def process_raw_order(self, order_json):
        new_order = OrderEntry(order_json)

        if new_order.is_buy_order():
            return self.process_buy_order(new_order)
        else:
            return self.process_sell_order(new_order)

    def process_sell_order(self, order: OrderEntry):
        self.sellOrders.insert(order)

    def process_buy_order(self, order: OrderEntry):
        self.buyOrders.insert(order)

    def to_json(self):
        return {
            "sellOrders": self.sellOrders.to_json(),
            "buyOrders": self.buyOrders.to_json(),
        }

    def __repr__(self):
        return json.dumps(self.__dict__)
