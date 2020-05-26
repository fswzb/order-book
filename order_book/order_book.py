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
        self.visible_quantity = 0 if self.is_iceberg else self.quantity

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

    def process_sell_order(self, sell_order: OrderEntry):
        # Fulfill existing orders
        while self.max_buy and sell_order.price <= self.max_buy:
            buy_offers = self.buy_orders[self.max_buy]

            while buy_offers:
                buy_offer = buy_offers[0]
                if buy_offer.quantity < sell_order.quantity:
                    OrderBook._broadcast_transaction(buy_offer.id, sell_order.id, self.max_buy, buy_offer.quantity)

                    sell_order.quantity -= buy_offer.quantity
                    buy_offers.popleft()
                else:
                    OrderBook._broadcast_transaction(buy_offer.id, sell_order.id, self.max_buy, sell_order.quantity)

                    if buy_offer.quantity > sell_order.quantity:
                        buy_offer.quantity -= sell_order.quantity
                    else:
                        buy_offers.popleft()

                    return  # Order fulfilled completely

            self.max_buy -= 1

        # Store unfulfilled part of the order
        self.sell_orders[sell_order.price].append(sell_order)
        if not self.min_sell or self.min_sell > sell_order.price:
            self.min_sell = sell_order.price

    def process_buy_order(self, buy_order: OrderEntry):
        # Fulfill existing orders
        while self.min_sell and buy_order.price >= self.min_sell:
            sell_offers = self.sell_orders[self.min_sell]

            while sell_offers:
                sell_offer = sell_offers[0]
                if sell_offer.quantity < buy_order.quantity:
                    OrderBook._broadcast_transaction(buy_order.id, sell_offer.id, self.min_sell, sell_offer.quantity)

                    buy_order.quantity -= sell_offer.quantity
                    sell_offers.popleft()
                else:
                    OrderBook._broadcast_transaction(buy_order.id, sell_offer.id, self.min_sell, buy_order.quantity)

                    if sell_offer.quantity > buy_order.quantity:
                        sell_offer.quantity -= buy_order.quantity
                    else:
                        sell_offers.popleft()

                    return  # Order fulfilled completely

            self.min_sell += 1

        # Store unfulfilled part of the order
        self.buy_orders[buy_order.price].append(buy_order)
        if not self.max_buy or self.max_buy < buy_order.price:
            self.max_buy = buy_order.price

    @staticmethod
    def _broadcast_transaction(buy_order_id: int, sell_order_id: int, price: int, quantity: int):
        info_dict = {
            "buyOrderId": buy_order_id,
            "sellOrderId": sell_order_id,
            "price": price,
            "quantity": quantity,
        }

        print(json.dumps(info_dict))

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
