from .websocket_server import start_server
import asyncio

if __name__ == '__main__':
    asyncio.run(start_server())