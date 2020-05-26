# Order book

Python implementation of simple order book for Limit and Iceberg order types.

## Requirements

- Python >= 3.7 (tested with 3.7.6)

## Usage

Run `python main.py` to start the order book with console input/output.

You can also examine tests directory to learn more about the usage 
and data format.

## Input

Each input line represents an order in JSON format. Program will stop 
reading after a blank line or EOF. Example input:

```json
{"type": "Limit", "order": {"direction": "Buy", "id": 1, "price": 14, "quantity": 20}}
{"type": "Iceberg", "order": {"direction": "Buy", "id": 2, "price": 15, "quantity": 50, "peak": 20}}
{"type": "Limit", "order": {"direction": "Sell", "id": 3, "price": 16, "quantity": 15}}
{"type": "Limit", "order": {"direction": "Sell", "id": 4, "price": 13, "quantity": 60}}
``` 

## Output

`main.py` will print order book state and executed transactions after every 
processed order.
