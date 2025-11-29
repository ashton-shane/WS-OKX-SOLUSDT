import asyncio
from helpers import get_conn_period, create_task_list, get_num_conn, process_queue, tabulate_scores, get_winner, get_file_name

async def main():
    # Get period of connection
    conn_period = get_conn_period()
    # Get number of parallel connections
    n = get_num_conn()
    # get CSV file name
    file_name = get_file_name()

    print("\n================================================================================\n")

    # Create an async queue to push trade objects
    queue = asyncio.Queue()

    # Dynamically create concurrent websocket sessions to the same channel, push to a list and await the tasks
    tasks = create_task_list(queue, conn_period, n)
    await asyncio.gather(*tasks) # * it is the splat operator that splits into separate tasks.
    
    # Add an end signaller for iteration later
    await queue.put(None)
    
    # get total connections to confirm
    print("\n------------------------ RESULTS -------------------------\n") # take away the first and last response (confirmation + signaller)

    # Note that the first response is always a confirmation of what you sent, followed by the actual data
    # Tabulate scores and get winner
    trades_dict = await process_queue(queue)
    scores_dict = tabulate_scores(trades_dict, n, file_name)
    get_winner(scores_dict)
    print("\n================================================================================\n")

if __name__ == "__main__":
    asyncio.run(main())