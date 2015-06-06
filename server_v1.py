__author__ = 'len'

import asyncio
import websockets
import json
import datetime

class server:
    def __init__(self):
        self.mode = input("Input the mode(winter/summer):")
        self.running_num = int(input("Input the max running number:"))
        self.info = {}
        self.mailbox = {}
        self.now_running_num = 0
        if self.mode == "winter":
            self.temp_max = 30
            self.temp_min = 25
        elif self.mode == "summer":
            self.temp_max = 25
            self.temp_min = 18

    @asyncio.coroutine
    def check_out(self,str1,websocket):
        if str1['cid'] in self.mailbox:
            if self.mailbox[str1['cid']]:
                encode = json.dumps({"method":"checkout","state":"shutdown"})
                yield from websocket.send(encode)
                rec = yield from websocket.recv()
                discode = json.loads(rec)
                if discode['result'] == "ok":
                    self.info[discode['cid']][3] = "checkout"
                    return 1
        return 0


    def record(self,cid,temp,speed,target,state,cost):
        self.info[cid] = [temp,speed,target,state,cost]

    def calculate_time(self,cid):#maybe useful or useless
        past_time = datetime.datetime.strptime(self.info[cid][5],'%Y-%m-%d %H:%M:%S')
        return (datetime.datetime.now()-past_time).seconds

    def calculate_now_temperature(self,cid):
        if self.info[cid][3] == "running":
            if self.mode == "winter":
                if self.info[cid][1] == "high":
                    now_temperature = self.info[cid][0] + self.calculate_time(cid)/10
                elif self.info[cid][1] == "medium":
                    now_temperature = self.info[cid][0] + self.calculate_time(cid)/15
                elif self.info[cid][1] == "low":
                    now_temperature = self.info[cid][0] + self.calculate_time(cid)/20
            elif self.mode == "summer":
                if self.info[cid][1] == "high":
                    now_temperature = self.info[cid][0] - self.calculate_time(cid)/10
                elif self.info[cid][1] == "medium":
                    now_temperature = self.info[cid][0] - self.calculate_time(cid)/15
                elif self.info[cid][1] == "low":
                    now_temperature = self.info[cid][0] - self.calculate_time(cid)/20
        else:
            now_temperature = self.info[cid][0]
        self.info[cid][0] = now_temperature
        return int(now_temperature)

    def calculate_cost(self,cid):
        if self.info[cid][3] == "running":
            timezone = (datetime.datetime.now()-datetime.datetime.strptime(self.info[cid][5],'%Y-%m-%d %H:%M:%S')).seconds
            if self.info[cid][1] == "high":
                cost = self.info[cid][4] + timezone/10
            elif self.info[cid][1] == "medium":
                cost = self.info[cid][4] + timezone/12
            elif self.info[cid][1] == "low":
                cost = self.info[cid][4] + timezone/15
        else:
            cost = self.info[cid][4]
        self.info[cid][4] = cost
        self.info[cid][5] = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S')
        return round(cost,2)

    def get_record_fromdatabase(self):
        pass

    @asyncio.coroutine
    def judge(self,str1,websocket):
        is_checkout = yield from self.check_out(str1,websocket)
        if is_checkout == 1:
            dealed = {}
        else:
            if str1['method'] =="handshake":
                self.record(str1['cid'],int(str1['temp']),str1['speed'],int(str1['target']),"running",0)
                dealed = {"method":"handshake","result":"ok","config":{"mode":self.mode,"temp-max":self.temp_max,"temp-min":self.temp_min},"state":"running"}
                time_str = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S')
                self.info[str1['cid']] = self.info[str1['cid']] + [time_str]
                self.now_running_num += 1
                self.info[str1['cid']][3] = "running"
            elif str1['method'] =="set":
                if self.mode == "winter":
                    if int(str1['target']) > self.info[str1['cid']][0]:
                        self.info[str1['cid']][1] = str1['speed']
                        self.info[str1['cid']][2] = int(str1['target'])
                        state = "running"
                        if self.info[str1['cid']][3] != "running":
                            self.now_running_num += 1
                            self.info[str1['cid']][3] = "running"
                            self.info[str1['cid']][5] = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S')
                    else:
                        self.info[str1['cid']][1] = str1['speed']
                        self.info[str1['cid']][2] = int(str1['target'])
                        state = "standby"
                        if self.info[str1['cid']][3] != "standby":
                            self.now_running_num -= 1
                            self.info[str1['cid']][3] = "standby"
                            self.info[str1['cid']][0] = self.calculate_now_temperature(str1['cid'])
                            self.info[str1['cid']][4] = self.calculate_cost(str1['cid'])
                            self.info[str1['cid']][5] = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S')
                else:
                    if int(str1['target']) < self.info[str1['cid']][0]:
                        self.info[str1['cid']][1] = str1['speed']
                        self.info[str1['cid']][2] = int(str1['target'])
                        state = "running"
                        if self.info[str1['cid']][3] != "running":
                            self.now_running_num += 1
                            self.info[str1['cid']][3] = "running"
                            self.info[str1['cid']][5] = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S')
                    else:
                        self.info[str1['cid']][1] = str1['speed']
                        self.info[str1['cid']][2] = int(str1['target'])
                        state = "standby"
                        if self.info[str1['cid']][3] != "standby":
                            self.now_running_num -= 1
                            self.info[str1['cid']][3] = "standby"
                            self.info[str1['cid']][0] = self.calculate_now_temperature(str1['cid'])
                            self.info[str1['cid']][4] = self.calculate_cost(str1['cid'])
                            self.info[str1['cid']][5] = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S')
                dealed = {"method":"set","state":state}
            elif str1['method'] =="get":
                temp = self.calculate_now_temperature(str1['cid'])
                if self.mode == "winter":
                    if temp >= self.info[str1['cid']][2]:
                        cost = self.calculate_cost(str1['cid'])
                        self.info[str1['cid']][3] = "standby"
                        state = "standby"
                        self.now_running_num -= 1
                    else:
                        state = "running"
                else:
                    if temp <= self.info[str1['cid']][2]:
                        self.info[str1['cid']][3] = "standby"
                        state = "standby"
                        self.now_running_num -= 1
                    else:
                        state = "running"
                cost = self.calculate_cost(str1['cid'])
                dealed = {"method":"get","temp":temp,"state":state,"cost":cost}
            elif str1['method'] =="changed":
                if self.mode == "winter":
                    if (int(str1['temp'])+2) >= self.info[str1['cid']][2]:
                        self.info[str1['cid']][0] = int(str1['temp'])
                        state = "standby"
                    else:
                        self.info[str1['cid']][0] = int(str1['temp'])
                        self.info[str1['cid']][3] = "running"
                        self.now_running_num += 1
                        state = "running"
                        self.info[str1['cid']][5] = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S')
                else:
                    if (int(str1['temp'])-2) <= self.info[str1['cid']][2]:
                        self.info[str1['cid']][0] = int(str1['temp'])
                        state = "standby"
                    else:
                        self.info[str1['cid']][0] = int(str1['temp'])
                        self.info[str1['cid']][3] = "running"
                        self.now_running_num += 1
                        state = "running"
                        self.info[str1['cid']][5] = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S')
                dealed = {"method":"changed","state":state}
            elif str1['method'] =="shutdown":
                if self.info[str1['cid']] == "running":
                    self.now_running_num -= 1
                    self.info[str1['cid']][3] = "shutdown"
                    self.info[str1['cid']][0] = self.calculate_now_temperature(str1['cid'])
                    self.info[str1['cid']][4] = self.calculate_cost(str1['cid'])
                    self.info[str1['cid']][5] = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S')
                else:
                    self.info[str1['cid']][3] = "shutdown"
                dealed = {"method":"shutdown","result":"ok","state":"shutdown"}
            elif str1['method'] == "record":
                dealed = self.get_record_fromdatabase()#needs completed
            elif str1['method'] == "checkout":
                dealed = {"method":"checkout","result":"ok"}
                self.mailbox[str1['cid']] = {"method":"checkout","state":"shutdown"}
                print(self.mailbox)
            return dealed

    @asyncio.coroutine
    def hello(self,websocket,path):
        var = 1
        if self.now_running_num < self.running_num:
            while var==1:
                decodejson = yield from websocket.recv()
                if decodejson == None:
                    break
                else:
                    rec = json.loads(decodejson)
                    print(rec)
                    dealed_str = yield from self.judge(rec,websocket)
                    print(dealed_str)
                    encodejson = json.dumps(dealed_str)
                    yield from websocket.send(encodejson)

s1 = server()
start_server = websockets.serve(s1.hello, 'localhost', 6666)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
