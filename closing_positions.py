from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
import threading
import time
import subprocess


class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.contract = Contract()
        self.order = Order()
        self.open_orders = []
        self.position = None

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextorderId = orderId
        print('The next valid order id is: ', self.nextorderId)

    def position(self, account, contract, pos, avgCost):
        super().position(account, contract, pos, avgCost)
        if pos != 0:
            self.position = (contract.symbol, contract.secType, contract.exchange, contract.currency)

    def openOrder(self, orderId, contract, order, orderState):
        super().openOrder(orderId, contract, order, orderState)
        self.open_orders.append(orderId)

    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId,
                    whyHeld, mktCapPrice):
        super().orderStatus(orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId,
                            whyHeld, mktCapPrice)
        if status == "Filled":
            if orderId in self.open_orders:
                self.open_orders.remove(orderId)

    def get_position(self):
        self.reqPositions()
        return self.position

    def close_all_positions(self):
        pos = self.get_position()
        if pos:
            symbol, secType, exchange, currency = pos
            self.contract.symbol = symbol
            self.contract.secType = secType
            self.contract.exchange = exchange
            self.contract.currency = currency
            self.order.action = "SELL" if pos[1] == "STK" else "BUY"
            self.order.totalQuantity = abs(pos[2])
            self.order.orderType = "MKT"
            self.placeOrder(self.nextorderId, self.contract, self.order)
        else:
            print("No positions to close")


app = IBapi()
app.connect('127.0.0.1', 4002, 0)

# Start the socket in a thread
api_thread = threading.Thread(target=app.run, daemon=True)
api_thread.start()

# Check if the API is connected via orderid
while True:
    if app.nextorderId > 0:
        print('connected')
        break

app.close_all_positions()
time.sleep(3)
app.disconnect()

subprocess.run(["python", "opening_positions.py"])
