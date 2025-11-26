import asyncio
from helpers import get_conn_period, get_winner, get_trades

async def main():
    conn_period = get_conn_period()
    print("\n================================================================================\n")

    # Create two queues
    queue_a = asyncio.Queue()
    queue_b = asyncio.Queue()

    # Create two concurrent websocket sessions to the same channel
    conn_a = asyncio.create_task(get_trades(queue_a, "A", conn_period))
    conn_b = asyncio.create_task(get_trades(queue_b, "B", conn_period))
    
    # Need to eventually await
    await conn_a
    await conn_b

    # get total connections to confirm
    print("\n------------------------ RESULTS -------------------------\n")
    print(f"Connection A received {queue_a.qsize()-2} responses")   # take away the first and last response (confirmation + signaller)
    print(f"Connection B received {queue_b.qsize()-2} responses")   

    # Remove from queues the first timestamp as that is the confirmation response
    await queue_a.get()
    await queue_b.get()

    # Tabulate scores and get winner
    await get_winner(queue_a, queue_b)


if __name__ == "__main__":
    asyncio.run(main())