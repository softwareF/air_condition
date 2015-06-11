__author__ = 'len'

import json
import asyncio
import websockets
import time

@asyncio.coroutine
def timer():
    websocket = yield from websockets.connect('ws://localhost:6666/')
    while 1:
        time.sleep(30)
        send_str = json.dumps({"method":"timer"})
        yield from websocket.send(send_str)

asyncio.get_event_loop().run_until_complete(timer())