from websockets.client import connect
import asyncio
import websockets
import json
import time

async def get_trades():
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

    # Establish first connection with websocket
    async with connect(uri) as websocket:
        # Send params to server
        await websocket.send(json.dumps(req_params, indent=4))

        # Calculate period of x seconds for loop to run
        now = time.perf_counter()
        end = now + 20

        # While loop to keep the data flowing until cancelled
        while end > time.perf_counter():
            # Note that the first response is always a confirmation of what you sent, followed by the actual data
            pong_waiter = await websocket.ping()
            recv_params = json.loads(await websocket.recv())
            print(recv_params)
            conn_a_latency = await pong_waiter
            print(f"connection A's latency is {conn_a_latency}")
            
        print("End of loop")
if __name__ == "__main__":
    asyncio.run(get_trades())