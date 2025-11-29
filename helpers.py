import json
import time
from websockets import connect
import asyncio
from collections import deque

def get_conn_period():
    while True:
        try:
            secs = int(input("Period (in seconds) to run websocket: ").strip())
            if isinstance(secs, int):
                return secs
        except ValueError:
            print("ERROR: Please only input an integer value")


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
            
            recv_data = json.loads(await websocket.recv())
            now = time.time() * 1000                                    # in miliseconds
            latency = now - (float(recv_data["data"][0]["ts"]))
            tradeId = recv_data["data"][0]["tradeId"]
            obj = {
                "connection": conn,
                "tradeId": tradeId,
                "latency": latency
            }
            print(obj)
            await queue.put(obj)       # push timestamp into queue with each response
        print(f"...connection {conn} responses stopped.")

def get_num_conn():
    while True:
        try:
            n = int(input("How many connections do you wish to start: "))
            if isinstance(n, int):
                return n
        except ValueError:
            print("ERROR: Please only input an integer value")
        
def create_task_list(queue, conn_period, n):
    task_list = []

    for i in range(n):
        task = asyncio.create_task(get_trades(queue, f"{i+1}", conn_period))
        task_list.append(task)
    return task_list


async def get_winner(queue):
    # create a trade ID queue, while the current trade ID is there, add to a hash table. 
    # the moment trade ID changes, popleft, and add new tradeID to begin cycle.
    # create hash table to tabulate scores then iterate
    arr = []
    curr_trade_id = deque(arr)


    scores = {}

    return

    print(f"There were draws")
    print(f"Connection A scored times while connection B scored {scores["B"]} times")
    print(f"Connection {winner} is the winner with {most} wins and was faster {diff} times!")
    print("\n================================================================================\n")