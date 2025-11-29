import asyncio
from helpers import get_conn_period, get_winner, get_trades, create_task_list, get_num_conn, process_queue

async def main():
    print("\n================================================================================\n")
    
    # Get period of connection
    conn_period = get_conn_period()
    # Get number of parallel connections
    n = get_num_conn()

    # Create an async queue to push timestamps
    queue = asyncio.Queue()

    # Dynamically create concurrent websocket sessions to the same channel, push to a list
    tasks = create_task_list(queue, conn_period, n)
    
    # Need to eventually await the list of tasks
    await asyncio.gather(*tasks) # * it is the splat operator that splits into separate tasks.
    
    # Add an end signaller for iteration later
    await queue.put(None)
    
    # get total connections to confirm
    print("\n------------------------ RESULTS -------------------------\n") # take away the first and last response (confirmation + signaller)

    # Note that the first response is always a confirmation of what you sent, followed by the actual data
    # Remove from queues the first timestamp as that is the confirmation response
    await queue.get()
    
    # Tabulate scores and get winner
    await process_queue(queue, n)


if __name__ == "__main__":
    asyncio.run(main())