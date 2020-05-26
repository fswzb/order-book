import json
from collections import deque, defaultdict
from typing import Deque, DefaultDict, Optional


class OrderEntry:
    def __init__(self, order_json):
        self.is_iceberg: bool = order_json['type'] == 'Iceberg'

        order = order_json['order']
        self.is_buy: bool = order['direction'] == 'Buy'
        self.id: int = order['id']
        self.price: int = order['price']
        self.quantity: int = order['quantity']
        self.peak: int = order.get('peak', None)

    def to_json(self):
        return {
            'id': self.id,
            'price': self.price,
            'quantity': self.quantity,
        }

    def __repr__(self):
        return json.dumps(self.__dict__)


class OrderBook:
    def __init__(self):
        # Group orders by it's price limit
        self.buy_orders: DefaultDict[int, Deque[OrderEntry]] = defaultdict(deque)
        self.sell_orders: DefaultDict[int, Deque[OrderEntry]] = defaultdict(deque)

        self.min_sell: Optional[int] = None
        self.max_buy: Optional[int] = None

    def process_raw_order(self, order_json):
        new_order = OrderEntry(order_json)

        if new_order.is_iceberg:
            # raise Exception("Not implemented")
            print("Iceberg not implemented")
            pass  # TODO implement

        if new_order.is_buy:
            return self.process_buy_order(new_order)
        else:
            return self.process_sell_order(new_order)

    def process_sell_order(self, order: OrderEntry):
        # Fulfill existing orders
        while self.max_buy and order.price <= self.max_buy:
            buy_offers = self.buy_orders[self.max_buy]
            self._execute_orders(order, buy_offers)

            self.max_buy -= 1

        # Store unfulfilled part of the order
        self.sell_orders[order.price].append(order)
        if not self.min_sell or self.min_sell > order.price:
            self.min_sell = order.price

    def process_buy_order(self, order: OrderEntry):
        # Fulfill existing orders
        while self.min_sell and order.price >= self.min_sell:
            sell_offers = self.sell_orders[self.min_sell]
            self._execute_orders(order, sell_offers)

            self.min_sell += 1

        # Store unfulfilled part of the order
        self.buy_orders[order.price].append(order)
        if not self.max_buy or self.max_buy < order.price:
            self.max_buy = order.price

    @staticmethod
    def _execute_orders(order: OrderEntry, offers: Deque[OrderEntry]):
        while offers:
            offer = offers[0]
            if offer.quantity < order.quantity:
                # Broadcast transaction made
                order.quantity -= offer.quantity
                offers.popleft()
            else:
                # Broadcast transaction made
                if offer.quantity > order.quantity:
                    offer.quantity -= order.quantity
                else:
                    offers.popleft()

                return  # Order fulfilled completely

    def to_json(self):
        return {
            "sellOrders": [order.to_json()
                           for sell_orders in self.sell_orders.values()
                           for order in list(sell_orders)],
            "buyOrders": [order.to_json()
                          for buy_orders in self.buy_orders.values()
                          for order in list(reversed(buy_orders))],
        }

    def __repr__(self):
        return json.dumps(self.__dict__)
