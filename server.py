__author__ = 'len'

import asyncio
import websockets
import json

class server:
    @asyncio.coroutine
    def record(self,cid,temp,speed,target):
        self.old_cid = cid
        self.old_temp = temp
        self.old_speed = speed
        self.old_target = target

    @asyncio.coroutine
    def season_mode(self): #needs completed
        season = "winter"
        return season

    @asyncio.coroutine
    def calculate_now_temperature(self):#needs completed
        now_temperature = 30
        return now_temperature

    @asyncio.coroutine
    def calculate_cost(self):
        #cost = time1*price1+time2*price2+time3*price3
        cost = 10
        return cost

    @asyncio.coroutine
    def judge(self,str):
        if str['method'] =="handshake":
            self.record(str['cid'],str['temp'],str['speed'],str['target'])
            mode = yield from self.season_mode()
            dealed = {"method":"handshake","result":"ok","config":{"mode":mode,"temp-max":[30],"temp-min":[25]},"state":"running"}
        elif str['method'] =="set":
            if str['target'] <= 30 and str['target'] >=25:
                state = "running"
            else:
                state = "standby"
            dealed = {"method":"set","state":state}
        elif str['method'] =="get":
            temp = yield from self.calculate_now_temperature()
            if temp == 30: #needs completed
                state = "standby"
            else:
                state = "running"
            cost = yield from self.calculate_cost()
            dealed = {"method":"get","temp":temp,"state":state,"cost":cost}
        elif str['method'] =="changed":
            if str['temp'] >= 30 or str['temp'] <= 25: #needs completed
                state = "standby"
            else:
                state = "running"
            dealed = {"method":"changed","state":state}
        elif str['method'] =="shutdown":
            #needs completed
            dealed = {"method":"shutdown","result":"ok","state":"shutdown"}
        elif str['method'] =="checkout":
            #needs completed
            dealed = {"method":"checkout","state":"shutdown"}
        return dealed

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

