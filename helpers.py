import json
import time
from websockets import connect
import asyncio

async def get_trades(queue, conn, secs):
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
        # Don't process the first websocket response
        await websocket.recv()

        # Calculate period of x seconds for loop to run
        start = time.perf_counter()
        end = start + secs

        # While loop to keep the data flowing until cancelled
        print(f"Connection {conn} receiving websocket responses from OKX...")
        while end > time.perf_counter():
            # Note that the first response is always a confirmation of what you sent, followed by the actual data
            recv_data = json.loads(await websocket.recv())
            now = time.time() * 1000       # in miliseconds
            latency = now - (float(recv_data["data"][0]["ts"]))
            print(f"Latency is {latency}")
            await queue.put(latency)       # push timestamp into queue with each response
        print(f"...connection {conn} responses stopped.")

        # Add an end signaller for iteration later
        await queue.put(None)

def get_conn_period():
    while True:
        try:
            secs = int(input("Period (in seconds) to run websocket: ").strip())
            if isinstance(secs, int):
                return secs
        except ValueError:
            print("ERROR: Please only input an integer value")


def create_task_list(queue, conn_period):
    while True:
        try:
            n = int(input("How many connections do you wish to start: "))
            if isinstance(n, int):
                break
        except ValueError:
            print("ERROR: Please only input an integer value")
        
        tasks = []
        for i in range(n):
            task = asyncio.create_task(get_trades(queue, f"{i}", conn_period))
            tasks.append(task)

    return tasks

async def get_winner(queue_a, queue_b):
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