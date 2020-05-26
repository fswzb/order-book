import json
import sys

from order_book.order_book import OrderBook


def main():
    order_book = OrderBook()

    for line in sys.stdin:
        if not line.rstrip():
            break

        json_line = json.loads(line.rstrip())

        executed_transactions = order_book.process_order(json_line)

        for t in executed_transactions:
            print(json.dumps(t))

        print(json.dumps(order_book.to_json()))


if __name__ == '__main__':
    main()
