from ibapi.client import EClient
from ibapi.wrapper import EWrapper
import subprocess
import json

def run_loop():
    app.run()

class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.nextorderId = None

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



