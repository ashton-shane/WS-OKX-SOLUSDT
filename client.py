import asyncio
from helpers import get_conn_period, get_winner, get_trades

async def main():
    conn_period = get_conn_period()
    print("\n================================================================================\n")

    # Create an async queue to push timestamps
    queue = asyncio.Queue()

    # Create two concurrent websocket sessions to the same channel
    n = input("How many connections do you wish to start: ")
    tasks = []
    for i in range(n):
        task = asyncio.create_task(get_trades(queue, f"{i}", conn_period))
        tasks.append(task)
    
    # Need to eventually await
    await asyncio.gather(*tasks) # * it is the splat operator that splits into separate tasks.=

    # get total connections to confirm
    print("\n------------------------ RESULTS -------------------------\n") # take away the first and last response (confirmation + signaller)

    # Remove from queues the first timestamp as that is the confirmation response
    await queue.get()

    # Tabulate scores and get winner
    await get_winner(queue)


if __name__ == "__main__":
    asyncio.run(main())