import json
from collections import deque, defaultdict
from typing import Deque, DefaultDict, Optional, Dict, List


class OrderEntry:
    """ A single exchange order.

        Recognized order types are Limit and Iceberg.
    """

    def __init__(self, order_json):
        self.is_iceberg: bool = order_json['type'] == 'Iceberg'

        order = order_json['order']
        self.is_buy: bool = order['direction'] == 'Buy'
        self.id: int = order['id']
        self.price: int = order['price']
        self.quantity: int = order['quantity']

        self.peak: int = order['peak'] if self.is_iceberg else 0
        self._visible_quantity = 0 if self.is_iceberg else self.quantity

    def _update_visible_quantity(self):
        if self.is_iceberg and self._visible_quantity == 0:
            reload = min(self.quantity, self.peak)
            self._visible_quantity = min(self.quantity, self.peak)
            self.quantity -= reload

    @property
    def visible_quantity(self):
        if self.is_iceberg:
            self._update_visible_quantity()
            return self._visible_quantity
        else:
            return self.quantity

    @visible_quantity.setter
    def visible_quantity(self, new_value: int):
        if self.is_iceberg:
            self._visible_quantity = new_value
            self._update_visible_quantity()
        else:
            self.quantity = new_value

    def to_json(self):
        return {
            'id': self.id,
            'price': self.price,
            'quantity': self.visible_quantity,
        }

    def __repr__(self):
        return json.dumps(self.__dict__)


class OrderBook:
    """ Exchange order book

        OrderBook stores all pending sell or buy orders.

        To handle incoming orders, call 'process_order' method. It will
        broadcast any transactions resulting from the added order.

        To print contents of buy and order books, call 'to_json' method
    """

    def __init__(self):
        # Group orders by it's price limit
        self.buy_orders: DefaultDict[int, Deque[OrderEntry]] = defaultdict(deque)
        self.sell_orders: DefaultDict[int, Deque[OrderEntry]] = defaultdict(deque)

        self.broadcast_messages: List[Dict] = []

        self.min_sell: Optional[int] = None
        self.max_buy: Optional[int] = None

    def process_order(self, order_json):
        """ Process new order and execute transactions
        :param order_json: New order (as JSON)
        :return: List of executed transactions metadata
        """
        new_order = OrderEntry(order_json)

        if new_order.is_buy:
            self._process_buy_order(new_order)
        else:
            self._process_sell_order(new_order)



        # Return transaction messages
        messages = self.broadcast_messages
        self.broadcast_messages = []
        return messages

    def _process_sell_order(self, sell_order: OrderEntry):
        # Fulfill existing orders
        while self.max_buy and sell_order.price <= self.max_buy:
            buy_offers = self.buy_orders[self.max_buy]

            while buy_offers:
                buy_offer = buy_offers[0]
                if buy_offer.visible_quantity <= sell_order.quantity:
                    self._broadcast_transaction(buy_offer.id, sell_order.id, self.max_buy, buy_offer.visible_quantity)

                    sell_order.quantity -= buy_offer.visible_quantity
                    buy_offer.visible_quantity = 0
                    buy_offers.popleft()
                    if buy_offer.visible_quantity > 0:
                        buy_offers.append(buy_offer)
                    if sell_order.quantity == 0:
                        return  # Order fulfilled completely
                else:
                    self._broadcast_transaction(buy_offer.id, sell_order.id, self.max_buy, sell_order.quantity)

                    buy_offer.visible_quantity -= sell_order.quantity

                    return  # Order fulfilled completely

            self.max_buy -= 1

        # Store unfulfilled part of the order
        self.sell_orders[sell_order.price].append(sell_order)
        if not self.min_sell or self.min_sell > sell_order.price:
            self.min_sell = sell_order.price

    def _process_buy_order(self, buy_order: OrderEntry):
        # Fulfill existing orders
        while self.min_sell and buy_order.price >= self.min_sell:
            sell_offers = self.sell_orders[self.min_sell]

            while sell_offers:
                sell_offer = sell_offers[0]
                if sell_offer.visible_quantity <= buy_order.quantity:
                    self._broadcast_transaction(buy_order.id, sell_offer.id, self.min_sell, sell_offer.visible_quantity)

                    buy_order.quantity -= sell_offer.visible_quantity
                    sell_offer.visible_quantity = 0
                    sell_offers.popleft()
                    if sell_offer.visible_quantity > 0:
                        sell_offers.append(sell_offer)
                    if buy_order.quantity == 0:
                        return  # Order fulfilled completely
                else:
                    self._broadcast_transaction(buy_order.id, sell_offer.id, self.min_sell, buy_order.quantity)

                    sell_offer.visible_quantity -= buy_order.quantity

                    return  # Order fulfilled completely

            self.min_sell += 1

        # Store unfulfilled part of the order
        self.buy_orders[buy_order.price].append(buy_order)
        if not self.max_buy or self.max_buy < buy_order.price:
            self.max_buy = buy_order.price

    def _broadcast_transaction(self, buy_order_id: int, sell_order_id: int, price: int, quantity: int):
        info_msg_dict = {
            "buyOrderId": buy_order_id,
            "sellOrderId": sell_order_id,
            "price": price,
            "quantity": quantity,
        }
        self.broadcast_messages.append(info_msg_dict)

    def to_json(self):
        return {
            "buyOrders": [order.to_json()
                          for (_, buy_orders) in sorted(self.buy_orders.items(), reverse=True)
                          for order in buy_orders],
            "sellOrders": [order.to_json()
                           for (_, sell_orders) in sorted(self.sell_orders.items())
                           for order in list(sell_orders)],
        }
