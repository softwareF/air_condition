__author__ = 'len'

import asyncio
import websockets
import json

class client:
    @asyncio.coroutine
    def sendandrecv(self):
        key = 1
        websocket = yield from websockets.connect('ws://localhost:6666/')
        if websocket is None:
            key = 0
        if key==1:
            #handshake
            method = input("Input the mothod:")
            cid = input("Input the cid:")
            temp = input("Input the temp temperature now:")
            speed = input("Input the speed:")
            target = input("Input the target temperature:")
            sendstr = {"mothod":method,"cid":cid,"temp":temp,"speed":speed,"target":target}
            encodejson = json.dumps(sendstr)
            yield from websocket.send(encodejson)
            print(sendstr)
            decodejson = yield from websocket.recv()
            greeting = json.loads(decodejson)
            print(greeting)
            while key==1:
                #other operations
                method = input("Input the mothod:")
                cid = input("Input the cid:")
                temp = input("Input the temp:")
                speed = input("Input the temp temperature now:")
                target = input("Input the target temperature:")
                sendstr = {"mothod":method,"cid":cid,"temp":temp,"speed":speed,"target":target}
                encodejson = json.dumps(sendstr)
                yield from websocket.send(encodejson)
                print(sendstr)
                decodejson = yield from websocket.recv()
                greeting = json.loads(decodejson)
                print(greeting)

user = client()
asyncio.get_event_loop().run_until_complete(user.sendandrecv())