import asyncio
import websockets
from websockets.asyncio.server import serve

async def handler(websocket):
    while True:
        message = await websocket.recv()
        print(message)
        
async def main():
    async with serve(handler, "", 8001) as server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())