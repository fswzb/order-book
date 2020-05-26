import unittest

from order_book.order_book import OrderBook


class TestOrderBook(unittest.TestCase):
    def setUp(self):
        self.order_book = OrderBook()

    def test_case_1(self):
        input = [
            {"type": "Limit", "order": {"direction": "Buy", "id": 1, "price": 14, "quantity": 20}},
            {"type": "Iceberg", "order": {"direction": "Buy", "id": 2, "price": 15, "quantity": 50, "peak": 20}},
            {"type": "Limit", "order": {"direction": "Sell", "id": 3, "price": 16, "quantity": 15}},
            {"type": "Limit", "order": {"direction": "Sell", "id": 4, "price": 13, "quantity": 60}}
        ]

        msgs = self.order_book.process_order(input[0])
        book_json = self.order_book.to_json()
        self.assertDictEqual({"buyOrders": [{"id": 1, "price": 14, "quantity": 20}], "sellOrders": []}, book_json)
        self.assertEqual(0, len(msgs))

        msgs = self.order_book.process_order(input[1])
        book_json = self.order_book.to_json()
        self.assertDictEqual(
            {"buyOrders": [{"id": 2, "price": 15, "quantity": 20}, {"id": 1, "price": 14, "quantity": 20}],
             "sellOrders": []}, book_json)
        self.assertEqual(0, len(msgs))

        msgs = self.order_book.process_order(input[2])
        book_json = self.order_book.to_json()
        self.assertDictEqual(
            {"buyOrders": [{"id": 2, "price": 15, "quantity": 20}, {"id": 1, "price": 14, "quantity": 20}],
             "sellOrders": [{"id": 3, "price": 16, "quantity": 15}]}, book_json)
        self.assertEqual(0, len(msgs))

        msgs = self.order_book.process_order(input[3])
        book_json = self.order_book.to_json()
        self.assertDictEqual({"buyOrders": [{"id": 1, "price": 14, "quantity": 10}],
                              "sellOrders": [{"id": 3, "price": 16, "quantity": 15}]}, book_json)
        self.assertEqual(4, len(msgs))
        self.assertDictEqual(msgs[0], {"buyOrderId": 2, "sellOrderId": 4, "price": 15, "quantity": 20})
        self.assertDictEqual(msgs[1], {"buyOrderId": 2, "sellOrderId": 4, "price": 15, "quantity": 20})
        self.assertDictEqual(msgs[2], {"buyOrderId": 2, "sellOrderId": 4, "price": 15, "quantity": 10})
        self.assertDictEqual(msgs[3], {"buyOrderId": 1, "sellOrderId": 4, "price": 14, "quantity": 10})

    def test_case_2(self):
        input = [
            {"type": "Iceberg", "order": {"direction": "Sell", "id": 1, "price": 100, "quantity": 200, "peak": 100}},
            {"type": "Iceberg", "order": {"direction": "Sell", "id": 2, "price": 100, "quantity": 300, "peak": 100}},
            {"type": "Iceberg", "order": {"direction": "Sell", "id": 3, "price": 100, "quantity": 200, "peak": 100}},
            {"type": "Iceberg", "order": {"direction": "Buy", "id": 4, "price": 100, "quantity": 500, "peak": 100}}
        ]

        msgs = self.order_book.process_order(input[0])
        book_json = self.order_book.to_json()
        self.assertDictEqual({"buyOrders": [], "sellOrders": [{"id": 1, "price": 100, "quantity": 100}]}, book_json)
        self.assertEqual(0, len(msgs))

        msgs = self.order_book.process_order(input[1])
        book_json = self.order_book.to_json()
        self.assertDictEqual({"buyOrders": [], "sellOrders": [{"id": 1, "price": 100, "quantity": 100},
                                                              {"id": 2, "price": 100, "quantity": 100}]}, book_json)
        self.assertEqual(0, len(msgs))

        msgs = self.order_book.process_order(input[2])
        book_json = self.order_book.to_json()
        self.assertDictEqual({"buyOrders": [], "sellOrders": [{"id": 1, "price": 100, "quantity": 100},
                                                              {"id": 2, "price": 100, "quantity": 100},
                                                              {"id": 3, "price": 100, "quantity": 100}]}, book_json)
        self.assertEqual(0, len(msgs))

        msgs = self.order_book.process_order(input[3])
        book_json = self.order_book.to_json()
        self.assertDictEqual({"buyOrders": [], "sellOrders": [{"id": 3, "price": 100, "quantity": 100},
                                                              {"id": 2, "price": 100, "quantity": 100}]}, book_json)
        self.assertEqual(5, len(msgs))
        self.assertDictEqual({"buyOrderId": 4, "sellOrderId": 1, "price": 100, "quantity": 100}, msgs[0])
        self.assertDictEqual({"buyOrderId": 4, "sellOrderId": 2, "price": 100, "quantity": 100}, msgs[1])
        self.assertDictEqual({"buyOrderId": 4, "sellOrderId": 3, "price": 100, "quantity": 100}, msgs[2])
        self.assertDictEqual({"buyOrderId": 4, "sellOrderId": 1, "price": 100, "quantity": 100}, msgs[3])
        self.assertDictEqual({"buyOrderId": 4, "sellOrderId": 2, "price": 100, "quantity": 100}, msgs[4])


if __name__ == '__main__':
    unittest.main()
