from typing import List


class OrderEntry:
    type_: str
    id: int
    price: int
    quantity: int
    direction: str
    peak: int

    def is_iceberg(self):
        return self.type_ == 'Iceberg'

    def to_json(self):
        return {
            'id': self.id,
            'price': self.id,
            'quantity': self.id,
        }


class OrderCollection:
    orders: List[OrderEntry]

    def to_json(self):
        return [o.to_json() for o in self.orders]


class OrderBook:
    buyOrders: OrderCollection = OrderCollection()
    sellOrders: OrderCollection = OrderCollection()

    def to_json(self):
        return {
            "sellOrders": self.sellOrders.to_json(),
            "buyOrders": self.buyOrders.to_json(),
        }
