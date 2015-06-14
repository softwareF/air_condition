__author__ = 'len'

import asyncio
import websockets
import json
import datetime
import queue
import pymysql

class server:
    def __init__(self):
        self.mode = input("Input the mode(winter/summer):")
        self.running_num = int(input("Input the max running number:"))
        self.info = {} #record the information of each rooms
        self.index = {} #record the user id and the room id
        self.socket = {} #record each socket
        self.flag = 1 #shutdown the socket if flag is 0
        self.now_running_num = 0
        self.regflg = 0
        self.gettemp = 0
        self.reportflg = 0
        self.finished = 0
        self.now_cost = 0
        self.myqueue = queue.PriorityQueue() #record the of self.info
        if self.mode == "winter":
            self.temp_max = 30
            self.temp_min = 25
        elif self.mode == "summer":
            self.temp_max = 25
            self.temp_min = 18

    def record_websocket(self,websocket,str1): #record the socket when handshake
        if str1['cid'] not in self.socket.keys():
            self.socket[str1['cid']] = websocket

    def is_registed(self,str1): #if not register then don't let the socket connected
        for key,value in self.index.items():
            if str1['cid'] == value[1]:
                return 1
        return 0

    def record(self,cid,temp,speed,target,state,cost):
        self.info[cid] = [temp,speed,target,state,cost]

    def calculate_time(self,cid): #calculate the seconds of the timezone
        past_time = datetime.datetime.strptime(self.info[cid][5],'%Y-%m-%d %H:%M:%S')
        return (datetime.datetime.now()-past_time).seconds

    def calculate_now_temperature(self,cid):
        if self.mode == "winter":
            if self.info[cid][1] == "high":
                now_temperature = self.info[cid][0] + round(self.calculate_time(cid)/60,2)
            elif self.info[cid][1] == "medium":
                now_temperature = self.info[cid][0] + round(self.calculate_time(cid)/120,2)
            elif self.info[cid][1] == "low":
                now_temperature = self.info[cid][0] + round(self.calculate_time(cid)/180,2)
        elif self.mode == "summer":
            if self.info[cid][1] == "high":
                now_temperature = self.info[cid][0] - round(self.calculate_time(cid)/60,2)
            elif self.info[cid][1] == "medium":
                now_temperature = self.info[cid][0] - round(self.calculate_time(cid)/120,2)
            elif self.info[cid][1] == "low":
                now_temperature = self.info[cid][0] - round(self.calculate_time(cid)/180,2)
        return now_temperature

    def calculate_cost(self,cid):
        timezone = (datetime.datetime.now()-datetime.datetime.strptime(self.info[cid][5],'%Y-%m-%d %H:%M:%S')).seconds
        if self.info[cid][1] == "high":
            cost = self.info[cid][4] + round(timezone/60,2)
        elif self.info[cid][1] == "medium":
            cost = self.info[cid][4] + round(timezone/120,2)
        elif self.info[cid][1] == "low":
            cost = self.info[cid][4] + round(timezone/180,2)
        return round(cost,2)

    def send_to_database(self,str1):
        if self.finished == 1:
            time_str = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S')
            database_exec = "insert into running_status (room_id,optime,optype,req_temp_start,req_temp_end,speed)values('" +str(str1['cid'])+"','"+str(time_str)+"','finish','"+str(self.info[str1['cid']][0])+"','"+str(self.info[str1['cid']][2])+"','"+str(self.info[str1['cid']][1])+"');"
            print(database_exec)
            sta=cur.execute(database_exec)
            self.finished = 0
        if str1['method'] =="handshake":
            time_str = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S')
            database_exec = "insert into running_status (room_id,optime,optype,req_temp_start,req_temp_end,speed)values('" +str(str1['cid'])+"','"+str(time_str)+"','on','"+str(str1['temp'])+"','"+str(str1['target'])+"','"+str1['speed']+"');"
            print(database_exec)
            sta=cur.execute(database_exec)
        elif str1['method'] =="set":
            time_str = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S')
            database_exec = "insert into running_status (room_id,optime,optype,req_temp_end,speed,req_temp_start)values('"+str(str1['cid'])+"','"+str(time_str)+"','set','"+str(str1['target'])+"','"+str1['speed']+"',"+str(self.info[str1['cid']][0])+");"
            print(database_exec)
            sta=cur.execute(database_exec)
        elif str1['method'] =="get":
            time_str = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S')
            database_exec = "insert into running_status (room_id,optime,optype,req_temp_start)values('"+str(str1['cid'])+"','"+str(time_str)+"','get',"+str(self.gettemp)+");"
            print(database_exec)
            sta=cur.execute(database_exec)
        elif str1['method'] =="changed":
            time_str = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S')
            database_exec = "insert into running_status (room_id,optime,optype,req_temp_start)values('"+str(str1['cid'])+"','"+str(time_str)+"','changed','"+str(str1['temp'])+"');"
            print(database_exec)
            sta=cur.execute(database_exec)
        elif str1['method'] =="shutdown":
            time_str = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S')
            database_exec = "insert into running_status (room_id,optime,optype)values('"+str(str1['cid'])+"','"+str(time_str)+"','off');"
            print(database_exec)
            sta=cur.execute(database_exec)
        elif str1['method'] == "report":
            database_exec = "select * from running_status where (room_id ='"+str1['cid'] +"' and (optype = 'set' or optype = 'finish' or optype = 'on' or optype = 'off'));"
            print(database_exec)
            cur.execute(database_exec)
            report_list = []
            for r in cur.fetchall():
                report_text = str(r)
                report_list += [report_text]
            dealed = {"method":"report","data":report_list,"result":"ok"}
            return dealed
        elif str1['method'] == "checkout":
            database_exec = "delete from user_data where (room_id ='"+str1['cid'] +"');"
            print(database_exec)
            cur.execute(database_exec)
            conn.commit()
        elif str1['method'] == "register":
            if self.regflg == 1:
                time_str = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S')
                database_exec = "insert into user_data (user_id,optime,room_id,username,money)values('"+str(str1['id'])+"','"+str(time_str)+"','"+str(str1['cid'])+"','"+str(str1['name'])+"',"+str(str1['money'])+");"
                print(database_exec)
                sta=cur.execute(database_exec)
                conn.commit()
        elif str1['method'] == "recharge":
            time_str = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S')
            database_exec = "update user_data set money = money +"+str(str1['money'])+" where user_id ="+str(str1['id'])+";"
            print(database_exec)
            sta=cur.execute(database_exec)
        database_exec = "select user_id from user_data where room_id = '"+str(str1['cid'])+"';"
        sta = cur.execute(database_exec)
        now_id = ''
        for each in cur:
           now_id = each[0]
        if now_id == '':
            return
        now_money = int(self.index[now_id][2]) - self.now_cost
        database_exec = "update user_data set money = "+str(now_money)+" where user_id ="+str(now_id)+";"
        print(database_exec)
        sta=cur.execute(database_exec)
        conn.commit()
        return

    def speed_to_int(self,speed): #the PriorityQueue is ordered from the smallest to the biggest
        if speed is "high":
            return 10000
        elif speed is "medium":
            return 20000
        else:
            return 30000

    def asyn(self):
        r = {}
        if self.now_running_num <= self.running_num:
            num = self.now_running_num
        else:
            num = self.running_num
        for i in range(num):
            r[num-i-1] = list(self.myqueue.get())
            cid = r[num-i-1][1]
            self.info[cid][0] = self.calculate_now_temperature(cid)
            self.info[cid][4] = self.calculate_cost(cid)
            if self.mode == "winter":
                if int(self.info[cid][0]) >= int(self.info[cid][2]):
                    self.info[cid][3] = "standby"
                    r[num-i-1] += ["no"]
                    self.now_running_num -= 1
                else:
                    self.info[cid][3] = "running"
                    r[num-i-1] += ["yes"]
            else:
                if int(self.info[cid][0]) <= int(self.info[cid][2]):
                    print(4)
                    self.info[cid][3] = "standby"
                    r[num-i-1] += ["no"]
                    self.now_running_num -= 1
                else:
                    self.info[cid][3] = "running"
                    r[num-i-1] += ["yes"]
        time_str = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S')
        if self.now_running_num is not 0:
            for key,value in self.info:
                self.info[key][5] = time_str
        for i in range(num):
            if r[i][2] == "yes":
                weight = self.speed_to_int(self.info[r[i][1]][1]) + int(datetime.datetime.strftime(datetime.datetime.now(),'%M'))*100 + int(datetime.datetime.strftime(datetime.datetime.now(),'%S'))
                self.myqueue.put((weight,r[i][1]))

    def putout_from_queue(self,cid): #if the sub-control air-condition is still running but shutdown , we should put out the info of it from the queue
        size = self.myqueue.qsize()
        for i in range(size):
            r[size-i] = self.myqueue.get()
            if cid is r[size-i][1]:
                r[size-i][2] = "no"
            else:
                r[size-i][2] = "yes"
        for i in range(size):
            if r[size-i][2] == "yes":
                self.myqueue.put((r[size-i][0],r[size-i][1]))

    def display(self):#send message to the special client for showing
        for key,value in self.info.items():
            cid = key
            temp = value[0]
            speed = value[1]
            targrt = value[2]
            state = value[3]
            cost = value[4]
            rest = self.index[key][2]-value[4]
            send = {"cid":cid,"temp":temp,"targrt":targrt,"state":state,"speed":speed,"cost":cost,"rest":rest}
            send = json.dumps(send)
            self.socket["display"].send(send)

    def judge(self,str1,websocket):
        self.reportflg = 0
        dealed = {}

        if str1['method'] =="timer":
            self.asyn()
            #self.display()

        elif str1['method'] =="handshake":
            if self.is_registed(str1):
                self.record_websocket(websocket,str1)
                self.record(str1['cid'],float(str1['temp']),str1['speed'],float(str1['target']),"running",0)
                dealed = {"method":"handshake","result":"ok","config":{"mode":self.mode,"temp-max":self.temp_max,"temp-min":self.temp_min},"state":"running"}
                time_str = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S')
                self.info[str1['cid']] = self.info[str1['cid']] + [time_str]
                weight = self.speed_to_int(str1['speed']) + int(datetime.datetime.strftime(datetime.datetime.now(),'%M'))*100 + int(datetime.datetime.strftime(datetime.datetime.now(),'%S'))
                self.myqueue.put((weight,str1['cid']))
                self.now_running_num += 1
                self.info[str1['cid']][3] = "running"
                #self.display()
            else:
                self.flag = 0

        elif str1['method'] =="set":
            self.info[str1['cid']][2] = float(str1['target'])
            self.info[str1['cid']][1] = str1['speed']
            state = self.info[str1['cid']][3]
            #self.display()
            dealed = {"method":"set","state":state}

        elif str1['method'] =="get":
            temp = int(self.info[str1['cid']][0])
            cost = self.info[str1['cid']][4]
            state = self.info[str1['cid']][3]
            #self.display()
            dealed = {"method":"get","temp":temp,"state":state,"cost":cost}

        elif str1['method'] =="changed":
            if self.mode == "winter":
                if (int(str1['temp'])+1) > int(self.info[str1['cid']][2]):
                    self.info[str1['cid']][0] = float(str1['temp'])
                    state = "standby"
                else:
                    self.info[str1['cid']][0] = float(str1['temp'])
                    self.info[str1['cid']][3] = "running"
                    self.info[str1['cid']][5] = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S')
                    weight = self.speed_to_int(str1['cid'][1]) + int(datetime.datetime.strftime(datetime.datetime.now(),'%M'))*100 + int(datetime.datetime.strftime(datetime.datetime.now(),'%S'))
                    self.myqueue.put((weight,str1['cid']))
                    self.now_running_num += 1
                    state = "running"
            else:
                if (int(str1['temp'])-1) < int(self.info[str1['cid']][2]):
                    self.info[str1['cid']][0] = float(str1['temp'])
                    state = "standby"
                else:
                    self.info[str1['cid']][0] = float(str1['temp'])
                    self.info[str1['cid']][3] = "running"
                    self.info[str1['cid']][5] = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S')
                    weight = self.speed_to_int(str1['cid'][1]) + int(datetime.datetime.strftime(datetime.datetime.now(),'%M'))*100 + int(datetime.datetime.strftime(datetime.datetime.now(),'%S'))
                    self.myqueue.put((weight,str1['cid']))
                    self.now_running_num += 1
                    state = "running"
            #self.display()
            dealed = {"method":"changed","state":state}

        elif str1['method'] =="shutdown":
            self.flag = 0
            if self.info[str1['cid']] == "running":
                self.now_running_num -= 1
                self.putout_from_queue(str1['cid'])
                self.info[str1['cid']][0] = self.calculate_now_temperature(str1['cid'])
                self.info[str1['cid']][3] = "shutdown"
                self.info[str1['cid']][4] = self.calculate_cost(str1['cid'])
                self.info[str1['cid']][5] = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S')
            else:
                self.info[str1['cid']][3] = "shutdown"
            #self.display()
            dealed = {"method":"shutdown","result":"ok","state":"shutdown"}

        elif str1['method'] == "report":
            self.reportflg = 1

        elif str1['method'] == "checkout":
            if self.info[str1['cid']] == "running":
                self.now_running_num -= 1
                self.putout_from_queue(str1['cid'])
                self.info[str1['cid']][0] = self.calculate_now_temperature(str1['cid'])
                self.info[str1['cid']][3] = "shutdown"
                self.info[str1['cid']][4] = self.calculate_cost(str1['cid'])
                self.info[str1['cid']][5] = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S')
            tflag = 0
            self.flag = 0
            for key1,value1 in self.index.items():
                if value1[1] == str1['cid']:
                    if str1['cid'] in self.info.keys():
                        del self.info[str1['cid']]
                        dealed = {"method":"checkout","state":"shutdown"}
                        encoded = json.dumps(dealed)
                        self.socket[str1['cid']].send(encoded) #don't use yield from here because yield will reduce a signal to make the program return back
                        self.socket[str1['cid']].recv()
                        tflag = 1
                        del self.index[key1]
                        break
            if tflag is 0:
                dealed = {"method":"checkout","result":"no"}
            else:
                dealed = {"method":"checkout","result":"ok"}
            #self.display()

        elif str1['method'] == "register":
            if str1['id'] not in self.index.keys():
                self.index[str1['id']] = [str1['name'],str1['cid'],str1['money']]
                dealed = {"result":"ok","method":"register"}
                self.regflg = 1
            else:
                dealed = {"result":"no","method":"register"}
                self.regflg = 0
            #self.display()

        elif str1['method'] == "recharge":
            if str1['id'] in self.index.keys():
                self.index[str1['id']][2] = str(int([str1['money']])+int(self.index[str1['id']][2]))
                dealed = {"result":"ok","method":"recharge"}
            else:
                dealed = {"result":"no","method":"recharge"}
            #self.display()

        return dealed

    @asyncio.coroutine
    def hello(self,websocket,path): #handler
        while True and self.flag:
            decodejson = yield from websocket.recv()
            if decodejson == None:
                break
            else:
                rec = json.loads(decodejson)
                print(rec)
                dealed_str = self.judge(rec,websocket)
                #if self.reportflg == 1:
                    #dealed_str = self.send_to_database(rec)
                #else:
                    #self.send_to_database(rec)
                print(dealed_str)
                encodejson = json.dumps(dealed_str)
                if self.flag:
                    yield from websocket.send(encodejson)
        self.flag = 1

s1 = server()
start_server = websockets.serve(s1.hello, '0.0.0.0', 8000) #use 0.0.0.0 and the port number must larger than 8000
#sql_name = "hotel_manage"
#sql_username = "root"
#sql_password = "2525698"
#conn=pymysql.connect(host='localhost',user=sql_username,passwd=sql_password,db=sql_name,charset='utf8')
#cur=conn.cursor()
#sta=cur.execute("delete from user_data")
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()