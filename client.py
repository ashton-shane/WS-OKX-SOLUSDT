from websockets.sync.client import connect
import json

def get_trades():
    # Initialise the required params for the API
    req_params = {
        "op": "subscribe",
        "args": [
            {
            "channel": "trades",
            "instId": "SOL-USDT"
            }
        ]
    }

    # Initialise uri to connect to OKX websocket server
    uri = "wss://ws.okx.com:8443/ws/v5/public"

    # Establish connection with websocket
    with connect(uri) as websocket:
        websocket.send(json.dumps(req_params, indent=4))

        # While loop to keep the data flowing until cancelled
        while True:
            # Note that the first response is always a confirmation of what you sent, followed by the actual data
            recv_params = json.loads(websocket.recv())
            print(recv_params)

if __name__ == "__main__":
    get_trades()