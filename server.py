__author__ = 'len'

import asyncio
import websockets
import json

class server:
    @asyncio.coroutine
    def judge(self,str):
        return  str
    @asyncio.coroutine
    def hello(self,websocket, path):
        var = 1
        while var==1:
            decodejson = yield from websocket.recv()
            rec = json.loads(decodejson)
            print(rec)
            dealed_str = yield from self.judge(rec)
            print(dealed_str)
            encodejson = json.dumps(dealed_str)
            yield from websocket.send(encodejson)


s1 = server()
start_server = websockets.serve(s1.hello, 'localhost', 6666)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

