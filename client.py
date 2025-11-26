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
        end = start + 10

        # While loop to keep the data flowing until cancelled
        print(f"Connection {x} receiving websocket responses from OKX...")
        while end > time.perf_counter():
            # Note that the first response is always a confirmation of what you sent, followed by the actual data
            json.loads(await websocket.recv())
            await queue.put(time.perf_counter())       # push timestamp into queue with each response
        print(f"...connection {x} responses stopped.")

        # Add an end signaller for iteration later
        await queue.put(None)

async def main():
    print("\n================================================================================\n")
    # Create two queues
    queue_a = asyncio.Queue()
    queue_b = asyncio.Queue()

    # Create two concurrent websocket sessions to the same channel
    conn_a = asyncio.create_task(get_trades(queue_a, "A"))
    conn_b = asyncio.create_task(get_trades(queue_b, "B"))
    
    # Need to eventually await
    await conn_a
    await conn_b

    # get total connections to confirm
    print("\n------------------------ RESULTS -------------------------\n")
    print(f"Connection A received {queue_a.qsize()-2} responses")   # take away the first and last response (confirmation + signaller)
    print(f"Connection B received {queue_b.qsize()-2} responses")   

    # Ignore first timestamp as that is the confirmation response
    await queue_a.get()
    await queue_b.get()

    # create hash table to tabulate scores then iterate
    scores = {"A" : 0, 
              "B" : 0, 
              "DRAW": 0}
    
    while True:
        # Get each values - queues need to be awaited even when getting because they are channels
        a, b = await asyncio.gather(queue_a.get(), queue_b.get())

        # Check for end signaller, and add end scores if necessary
        if not a and not b:
            break
        elif b and not a:
            scores["B"] += 1    # means be managed to squeeze in one more connection before it closed
        elif a and not b:
            scores["A"] += 1

        # populate hash table with wins
        if a < b:
            scores["A"] += 1
        elif b < a:
            scores["B"] += 1
        else:
            scores["DRAW"] += 1

    # determine winner
    most = max(scores["A"], scores["B"])
    winner = next(k for k,v in scores.items() if scores[k] == most)
    diff = abs(scores["A"] - scores["B"])

    print(f"There were {scores['DRAW']} draws")
    print(f"Connection A scored {scores["A"]} times while connection B scored {scores["B"]} times")
    print(f"Connection {winner} is the winner with {most} wins and was faster {diff} times!")
    print("\n================================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())