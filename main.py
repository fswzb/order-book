import json
import sys

from order_book.order_book import OrderBook


def main():
    order_book = OrderBook()

    for line in sys.stdin:
        if not line.rstrip():
            break

        json_line = json.loads(line.rstrip())

        order_book.process_order(json_line)

        print(json.dumps(order_book.to_json()))


if __name__ == '__main__':
    main()
