def get_conn_period():
    while True:
        try:
            secs = int(input("Period (in seconds) to run websocket: ").strip())
            if isinstance(secs, int):
                return secs
        except ValueError:
            print("ERROR: Please only input an integer value")