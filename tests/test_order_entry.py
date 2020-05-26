import unittest

from order_book.order_book import OrderEntry


class TestOrderEntry(unittest.TestCase):
    def test_construct_limit_order_sell(self):
        json = {"type": "Limit", "order": {"direction": "Sell", "id": 1, "price": 101, "quantity": 20000}}
        order = OrderEntry(json)

        self.assertFalse(order.is_iceberg)
        self.assertFalse(order.is_buy)
        self.assertEqual(json['order']['id'], order.id)
        self.assertEqual(json['order']['price'], order.price)
        self.assertEqual(json['order']['quantity'], order.quantity)
        self.assertEqual(json['order']['quantity'], order.visible_quantity)

    def test_construct_limit_order_buy(self):
        json = {"type": "Limit", "order": {"direction": "Buy", "id": 1, "price": 14, "quantity": 20}}
        order = OrderEntry(json)

        self.assertFalse(order.is_iceberg)
        self.assertTrue(order.is_buy)
        self.assertEqual(json['order']['id'], order.id)
        self.assertEqual(json['order']['price'], order.price)
        self.assertEqual(json['order']['quantity'], order.quantity)
        self.assertEqual(json['order']['quantity'], order.visible_quantity)

    def test_construct_iceberg_order(self):
        json = {"type": "Iceberg", "order": {"direction": "Buy", "id": 2, "price": 15, "quantity": 50, "peak": 20}}
        order = OrderEntry(json)

        self.assertTrue(order.is_iceberg)
        self.assertTrue(order.is_buy)
        self.assertEqual(json['order']['id'], order.id)
        self.assertEqual(json['order']['price'], order.price)
        self.assertEqual(json['order']['quantity'], order.quantity)
        self.assertEqual(json['order']['peak'], order.peak)
        self.assertEqual(json['order']['peak'], order.visible_quantity)

    def test_to_json_limit_order(self):
        json = {"type": "Limit", "order": {"direction": "Buy", "id": 1, "price": 14, "quantity": 20}}
        expected = {"id": json['order']['id'], "price": json['order']['price'], "quantity": json['order']['quantity']}
        order = OrderEntry(json)

        self.assertDictEqual(expected, order.to_json())

    def test_to_json_iceberg_order(self):
        json = {"type": "Iceberg", "order": {"direction": "Buy", "id": 2, "price": 15, "quantity": 50, "peak": 20}}
        expected = {"id": json['order']['id'], "price": json['order']['price'], "quantity": json['order']['peak']}
        order = OrderEntry(json)

        self.assertDictEqual(expected, order.to_json())

    def test_visible_quantity_limit_order(self):
        json = {"type": "Limit", "order": {"direction": "Buy", "id": 1, "price": 14, "quantity": 20}}
        order = OrderEntry(json)

        self.assertEqual(20, order.visible_quantity)
        order.visible_quantity -= 10
        self.assertEqual(10, order.visible_quantity)
        order.visible_quantity -= 10
        self.assertEqual(0, order.visible_quantity)

    def test_visible_quantity_iceberg_order(self):
        json = {"type": "Iceberg", "order": {"direction": "Buy", "id": 2, "price": 15, "quantity": 50, "peak": 20}}
        order = OrderEntry(json)

        self.assertEqual(20, order.visible_quantity)
        order.visible_quantity -= 10
        self.assertEqual(10, order.visible_quantity)
        order.visible_quantity = 0
        self.assertEqual(20, order.visible_quantity)
        order.visible_quantity = 0
        self.assertEqual(10, order.visible_quantity)
        order.visible_quantity = 0
        self.assertEqual(0, order.visible_quantity)


if __name__ == '__main__':
    unittest.main()
