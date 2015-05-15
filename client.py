__author__ = 'len'

import asyncio
import websockets
import json

class client:
    def new_temperature(self):
        return 20 #needs completed

    @asyncio.coroutine
    def input_temp(self):
        method = input("Input the mothod:")
        if method == "handshake":
            target = input("Input the target temperature:")
            dealed = {"method":"handshake","cid":[1],"temp":[20],"speed":"low","target":target}
        elif method == "set":
            target = input("Input the target temperature:")
            speed = input("Input the new speed:")
            dealed = {"method":"set","cid":[1],"target":target,"speed":speed}
        elif method == "get":
            dealed = {"method":"get","cid":[1]}
        elif method == "changed":
            temp = self.new_temperature()
            dealed = {"method":"changed","cid":[1],"temp":[tmep]}
        elif method == "shutdown":
            dealed = {"method":"shutdown","cid":[1]}
        elif method == "checkout":
            dealed = {"method":"checkout","cid":[1],"result":"ok"}
        return dealed

    @asyncio.coroutine
    def sendandrecv(self):
        key = 1
        websocket = yield from websockets.connect('ws://localhost:6666/')
        if websocket is None:
            key = 0
        if key==1:
            #handshake
            sendstr = yield from self.input_temp()
            encodejson = json.dumps(sendstr)
            yield from websocket.send(encodejson)
            print(sendstr)
            decodejson = yield from websocket.recv()
            greeting = json.loads(decodejson)
            print(greeting)
            while key==1:
                #other operations
                sendstr = yield from self.input_temp()
                encodejson = json.dumps(sendstr)
                yield from websocket.send(encodejson)
                print(sendstr)
                decodejson = yield from websocket.recv()
                greeting = json.loads(decodejson)
                print(greeting)

user = client()
asyncio.get_event_loop().run_until_complete(user.sendandrecv())