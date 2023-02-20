from ibapi.client import EClient
from ibapi.wrapper import EWrapper
import subprocess
import json
from ibapi.contract import Contract
from ibapi.order import Order
import threading
import time
import csv

class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.nextorderId = None
        self.positions = [] # Add this line to initialize the positions list

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextorderId = orderId
        print('The next valid order id is: ', self.nextorderId)

    def orderStatus(self, orderId, status, filled, remaining, avgFullPrice, permId, parentId, lastFillPrice, clientId,
                    whyHeld, mktCapPrice):
        print('orderStatus - orderid:', orderId, 'status:', status, 'filled', filled, 'remaining', remaining,
              'lastFillPrice', lastFillPrice)

    def openOrder(self, orderId, contract, order, orderState):
        print('openOrder id:', orderId, contract.symbol, contract.secType, '@', contract.exchange, ':', order.action,
              order.orderType, order.totalQuantity, orderState.status)

    def execDetails(self, reqId, contract, execution):
        print('Order Executed: ', reqId, contract.symbol, contract.secType, contract.currency, execution.execId,
              execution.orderId, execution.shares, execution.lastLiquidity)

# Define a function to close all open positions
def close_all_positions(app):
    # Retrieve all open positions
    app.reqPositions()
    time.sleep(1)
    # Iterate over the open positions and close each position
    for pos in app.positions:
        order = Order()
        order.action = 'SELL' if pos.position > 0 else 'BUY'
        order.totalQuantity = abs(pos.position)
        order.orderType = 'MKT'
        app.placeOrder(app.nextorderId, pos.contract, order)
        app.nextorderId += 1
        time.sleep(1)
        print('Closed position for', pos.contract.symbol)

def run_loop():
    app.run()

# Listen for incoming webhook data
url = "https://api.pipedream.com/sources/dc_2Eu7X4x/sse"
auth_header = "Authorization: Bearer 360d90f4549def76cc1e370e71832b67"
curl_cmd = ["curl", "-s", "-N", "-H", auth_header, url]
proc = subprocess.Popen(curl_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
for line in proc.stdout:
    # Ignore any SSE data that isn't JSON-formatted
    if line.startswith(b"data: {"):
        # Strip the "data: " prefix from the line and parse the JSON-formatted data
        event_data = json.loads(line[6:])
        # Process the event data as needed
        data = event_data
        body = data['event']['body']
        symbol_fields = body.split(',')
        print(symbol_fields[0])
        print(symbol_fields[1])
        print(symbol_fields[2])
        print(symbol_fields[3])
        print(symbol_fields[4])
        print(symbol_fields[5])
        print(symbol_fields[6])
        filename = 'symbol_fields.csv'
        with open('symbol_fields.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            for row in data:
                writer.writerow(row)

        def options_order(symbol):
            contract = Contract()
            contract.symbol = symbol_fields[0]
            contract.secType = symbol_fields[1]
            contract.exchange = symbol_fields[2]
            contract.currency = symbol_fields[3]
            contract.lastTradeDateOrContractMonth = symbol_fields[4]
            contract.strike = symbol_fields[5]
            contract.right = symbol_fields[6]
            contract.multiplier = symbol_fields[7]
            return contract

        app = IBapi()
        app.connect('127.0.0.1', 4002, 123)

        app.nextorderId = None

        # Start the socket in a thread
        api_thread = threading.Thread(target=run_loop, daemon=True)
        api_thread.start()

        # Check if the API is connected via orderid
        while True:
            if isinstance(app.nextorderId, int):
                print('connected')
                break
            else:
                print('waiting for connection')
                time.sleep(1)

        # Create order object
        contract = options_order(symbol_fields)
        order = Order()
        order.action = 'BUY'
        order.totalQuantity = 1
        order.orderType = 'MKT'
        order.eTradeOnly = ''
        order.firmQuoteOnly = ''

        # Place order
        app.placeOrder(app.nextorderId, options_order('TSLA'), order)
        # app.nextorderId += 1

        time.sleep(3)

        # Cancel order
        #print('cancelling order')
        #app.cancelOrder(app.nextorderId)

        time.sleep(3)
        app.disconnect()