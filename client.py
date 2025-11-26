import asyncio
from websockets import connect
import json
import time


async def get_trades(queue, x):
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
        await websocket.send(json.dumps(req_params))

        # Calculate period of x seconds for loop to run
        start = time.perf_counter()
        end = start + 20

        # While loop to keep the data flowing until cancelled
        print("Receiving websocket requests...")
        while end > time.perf_counter():
            # Note that the first response is always a confirmation of what you sent, followed by the actual data
            json.loads(await websocket.recv())
            return_timestamp = time.perf_counter()  # get timestmap at which response is received
            await queue.put(return_timestamp)       # push timestamp into queue
            print(f"Connection {x} returned at {return_timestamp}")
        print("...requests stopped.")

async def main():
    # Create two queues
    queue_a = asyncio.Queue()
    queue_b = asyncio.Queue()

    # Create two concurrent websocket sessions to the same channel
    conn_a = asyncio.create_task(get_trades(queue_a, "A"))
    conn_b = asyncio.create_task(get_trades(queue_b, "B"))

    # Need to eventually await
    await conn_a
    await conn_b
    print(queue_a)
    print(queue_b)
    
    # create hash table to tabulate scores then iterate
    scores = {"A" : 0, "B" : 0}
    for i in range(queue_a.qsize):
        if queue_a[i] < queue_b[i]:
            scores["A"] += 1
        elif queue_a[i] < queue_b[i]:
            scores["B"] += 1

    # determine winner
    winner = max(scores["A"], scores["B"])
    diff = abs(scores["A"] - scores["B"])
    print("A")


if __name__ == "__main__":
    asyncio.run(main())