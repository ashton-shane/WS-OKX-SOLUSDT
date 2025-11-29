import json
import time
from websockets import connect
import asyncio
import pprint
import csv
import re

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


def get_file_name():
    while True:
        file_name = input("Please input your file name: ").strip().replace(" ", "")
        if re.fullmatch(r"[A-Za-z0-9_]+", file_name):
            return file_name


def create_task_list(queue, conn_period, n):
    task_list = []

    for i in range(n):
        task = asyncio.create_task(get_trades(queue, f"{i+1}", conn_period))
        task_list.append(task)
    return task_list


async def process_queue(queue): 
    # Create a dict of dicts organised by tradeIDs, 
    # i.e. {'394490182' : 
    #               {
    #                   '1' : 54.9580078125,
    #                   '2' : 55.9580078125
    #               }
    #       }

    trades_by_id = {}
    while True:
        # get next transaction
        curr = await queue.get()
        
        # Break once we hit the None signaller
        if not curr:
            break
        
        # populate dict
        curr_trade_id = curr["tradeId"]
        if not curr_trade_id in trades_by_id:
            trades_by_id[curr_trade_id] = { curr["connection"] : curr["latency"] }
        
        # Map latencies dict in dicts
        trades_by_id[curr_trade_id][curr["connection"]] = curr["latency"]
    return trades_by_id

def tabulate_scores(trades_dict, n, file_name):
    # create hash table to save scores
    scores = {}
    for i in range(n):
        scores[f"{i+1}"] = 0

    # tabulate
    winners = [] # for CSV purposes
    for i, trades in enumerate(trades_dict.items()):
        # "trades" is a tuple of (id : latency)
        winner = min(trades[1], key=trades[1].get)
        winners.append(winner)
        scores[winner] += 1
        print(f"The winner for trade {trades[0]} is connection {winner}")
    print(winners)
    # create CSV at this point
    write_to_csv(n, trades_dict, winners, file_name)

    # return scores
    return scores


def write_to_csv(n, trades_dict, winners, file_name):
    with open(f"{file_name}.csv", 'w', newline='') as csvfile:
        # ['tradeId', 'conn_1', 'conn_2', 'winner']
        fieldnames = ['no.', 'tradeId']
        for i in range(n):
            fieldnames.append(f"conn_{i+1}")
        fieldnames.append("winner")
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
    
        # write rows
        for i, (trade_id, trades) in enumerate(trades_dict.items()):
            # initialise row variable to store row KV pairs starting w tradeId
            row = { 
                'no.' : i+1,
                'tradeId' : trade_id }
            # for each ID, iterate through the connections
            for conn, latency in trades.items():
                row[f"conn_{conn}"] = latency
            # grab winner from winners array - indexes should follow the same as the trades_dict
            row["winner"] = winners[i]
            writer.writerow(row)
        
    print(f"{file_name}.csv has been successfully created!")

def get_winner(scores):
    overall_winner = max(scores, key=scores.get)
    print(f"\nThe overall winner is CONNECTION {overall_winner} with {scores[overall_winner]} wins!\n")