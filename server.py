__author__ = 'len'

import asyncio
import websockets
import json
import datetime
import pymysql

class server:
    def __init__(self):
        self.mode = input("Input the mode(winter/summer):")
        self.running_num = int(input("Input the max running number:"))+2
        self.info = {}
        self.index = {}
        self.socket = {}
        self.flag = 1
        self.now_running_num = 0
        self.regflg = 0
        self.gettemp = 0
        self.reportflg = 0
        self.finished = 0
        self.now_cost = 0
        if self.mode == "winter":
            self.temp_max = 30
            self.temp_min = 25
        elif self.mode == "summer":
            self.temp_max = 25
            self.temp_min = 18

    def record_websocket(self,websocket,str1):
        if str1['cid'] not in self.socket.keys():
            self.socket[str1['cid']] = websocket

    def asyn(self):
        pass

    def is_registed(self,str1):
        for key,value in self.index.items():
            if str1['cid'] == value[1]:
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
                    now_temperature = self.info[cid][0] + self.calculate_time(cid)/20
                elif self.info[cid][1] == "medium":
                    now_temperature = self.info[cid][0] + self.calculate_time(cid)/30
                elif self.info[cid][1] == "low":
                    now_temperature = self.info[cid][0] + self.calculate_time(cid)/60
            elif self.mode == "summer":
                if self.info[cid][1] == "high":
                    now_temperature = self.info[cid][0] - self.calculate_time(cid)/20
                elif self.info[cid][1] == "medium":
                    now_temperature = self.info[cid][0] - self.calculate_time(cid)/30
                elif self.info[cid][1] == "low":
                    now_temperature = self.info[cid][0] - self.calculate_time(cid)/60
        else:
            now_temperature = self.info[cid][0]
        self.info[cid][0] = now_temperature
        return int(now_temperature)

    def calculate_cost(self,cid):
        if self.info[cid][3] == "running":
            timezone = (datetime.datetime.now()-datetime.datetime.strptime(self.info[cid][5],'%Y-%m-%d %H:%M:%S')).seconds
            if self.info[cid][1] == "high":
                cost = self.info[cid][4] + timezone/20
            elif self.info[cid][1] == "medium":
                cost = self.info[cid][4] + timezone/30
            elif self.info[cid][1] == "low":
                cost = self.info[cid][4] + timezone/60
        else:
            cost = self.info[cid][4]
        self.info[cid][4] = cost
        self.info[cid][5] = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S')
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

    def judge(self,str1,websocket):
        self.reportflg = 0
        dealed = {}
        if str1['method'] == "timer":
            self.asyn()

        elif str1['method'] =="handshake":
            if self.is_registed(str1):
                self.record_websocket(websocket,str1)
                self.record(str1['cid'],int(str1['temp']),str1['speed'],int(str1['target']),"running",0)
                dealed = {"method":"handshake","result":"ok","config":{"mode":self.mode,"temp-max":self.temp_max,"temp-min":self.temp_min},"state":"running"}
                time_str = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S')
                self.info[str1['cid']] = self.info[str1['cid']] + [time_str]
                self.now_running_num += 1
                self.info[str1['cid']][3] = "running"
            else:
                self.flag = 0

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
            self.gettemp = temp
            if self.mode == "winter":
                if temp >= self.info[str1['cid']][2]:
                    self.finished = 1
                    cost = self.calculate_cost(str1['cid'])
                    self.info[str1['cid']][3] = "standby"
                    state = "standby"
                    self.now_running_num -= 1
                else:
                    self.finished = 0
                    state = "running"
            else:
                if temp <= self.info[str1['cid']][2]:
                    self.finished = 1
                    self.info[str1['cid']][3] = "standby"
                    state = "standby"
                    self.now_running_num -= 1
                else:
                    self.finished = 0
                    state = "running"
            cost = self.calculate_cost(str1['cid'])
            for (tkey,tvalue) in self.index.items():
                if str1['cid'] == tvalue[1]:
                    if cost >= int(tvalue[2]):
                        self.flag = 0
            self.now_cost = cost
            dealed = {"method":"get","temp":temp,"state":state,"cost":cost}

        elif str1['method'] =="changed":
            if self.mode == "winter":
                if (int(str1['temp'])) >= self.info[str1['cid']][2]:
                    self.info[str1['cid']][0] = int(str1['temp'])
                    state = "standby"
                else:
                    self.info[str1['cid']][0] = int(str1['temp'])
                    self.info[str1['cid']][3] = "running"
                    self.now_running_num += 1
                    state = "running"
                    self.info[str1['cid']][5] = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S')
            else:
                if (int(str1['temp'])) <= self.info[str1['cid']][2]:
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
        elif str1['method'] == "report":
            self.reportflg = 1

        elif str1['method'] == "checkout":
            tflag = 0
            for key1,value1 in self.index.items():
                if value1[1] == str1['cid']:
                    if str1['cid'] in self.info.keys():
                        del self.info[str1['cid']]
                        dealed = {"method":"checkout","state":"shutdown"}
                        encoded = json.dumps(dealed)
                        self.socket[str1['cid']].send(encoded)
                        self.socket[str1['cid']].recv()
                        tflag = 1
                        del self.index[key1]
                        break
            if tflag is 0:
                dealed = {"method":"checkout","result":"no"}
            else:
                dealed = {"method":"checkout","result":"ok"}

        elif str1['method'] == "register":
            if str1['id'] not in self.index.keys():
                self.index[str1['id']] = [str1['name'],str1['cid'],str1['money']]
                dealed = {"result":"ok","method":"register"}
                self.regflg = 1
            else:
                dealed = {"result":"no","method":"register"}
                self.regflg = 0

        elif str1['method'] == "recharge":
            if str1['id'] in self.index.keys():
                self.index[str1['id']][2] = str(int([str1['money']])+int(self.index[str1['id']][2]))
                dealed = {"result":"ok","method":"recharge"}
            else:
                dealed = {"result":"no","method":"recharge"}

        return dealed

    @asyncio.coroutine
    def hello(self,websocket,path):
        if self.now_running_num < self.running_num:
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

#sql_name = "hotel_manage"
#sql_username = "root"
#sql_password = "2525698"
#conn=pymysql.connect(host='localhost',user=sql_username,passwd=sql_password,db=sql_name,charset='utf8')
#cur=conn.cursor()
#sta=cur.execute("delete from user_data")
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()