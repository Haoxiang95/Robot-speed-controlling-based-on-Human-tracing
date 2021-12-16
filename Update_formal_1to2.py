# 开发时间: 2021-11-08 14:43
import threading
import time
import queue
from queue import Queue
import copy
import requests, json
import math
import time
import paho.mqtt.client as mqtt
import json
import ssl
from itertools import cycle

headers2= { 'Content-Type' : 'application/json',
            'id' : '2078',
            'Accept-Language' : 'en_US',
            'Authorization' : 'Basic RGlzdHJpYnV0b3I6NjJmMmYwZjFlZmYxMGQzMTUyYzk1ZjZmMDU5NjU3NmU0ODJiYjhlNDQ4MDY0MzNmNGNmOTI5NzkyODM0YjAxNA=='}
body1 = {
    "value": "1.1"
}
body2 = {
    "value": "0.5"
}
body3 = {
    "value": "0.25"
}
body4 = {
    "value": "0.15"
}

class MiR():
    def __init__(self):
        self.host = "http://192.168.100.51/api/v2.0.0/"
        self.headers = {}
        self.headers['Content-Type'] = 'application/json'
        self.headers['Accept-Language'] = 'en_US'
        # self.headers[
        #     'Authorization'] = 'Basic RGlzdHJpYnV0b3I6NjJmMmYwZjFlZmYxMGQzMTUyYzk1ZjZmMDU5NjU3NmU0ODJiYjhlNDQ4MDY0MzNmNGNmOTI5NzkyODM0YjAxNA=='
        self.headers[
            'Authorization'] = 'Basic RGlzdHJpYnV0b3I6NjJmMmYwZjFlZmYxMGQzMTUyYzk1ZjZmMDU5NjU3NmU0ODJiYjhlNDQ4MDY0MzNmNGNmOTI5NzkyODM0YjAxNA=='
        self.group_id = 'mirconst-guid-0000-0004-users0000000'
        # self.headers[
        #     'Authorization'] = 'Basic YWRtaW46OGM2OTc2ZTViNTQxMDQxNWJkZTkwOGJkNGRlZTE1ZGZiMTY3YTljODczZmM0YmI4YTgxZjZmMmFiNDQ4YTkxOA=='
        # self.group_id = 'mirconst-guid-0000-0011-missiongroup'
        # self.session_id = 'a2f5b1e6-d558-11ea-a95c-0001299f04e5'

    # Get the system information
    def get_system_info(self):
        try:
            result = requests.get(self.host + 'status', headers=self.headers)
            robot_json = result.json()
            self.robot_x = robot_json['position']['x']
            self.robot_y = robot_json['position']['y']
            #print('position x', self.robot_x, 'position y', self.robot_y, end='\n')
            #print(result)
        except:
            return 'No Connection'
        return result.json()

    def show_x(self):
        # self.x0 = x0
        self.get_system_info()
        #print(self.robot_x)
        return self.robot_x

    def show_y(self):
        # self.y0 = y0
        self.get_system_info()
        return self.robot_y


host = "172.27.15.23"  # fill in the IP of your gateway
port = 1883
topic = "tags"
client = mqtt.Client()
q=Queue()


def on_connect(client, userdata, flags, rc):
    print(mqtt.connack_string(rc))


def on_message_1(client, userdata, msg):
    global q
    #q = Queue(maxsize=2)
    # time.sleep(0.5)
    parsed_json = (json.loads(msg.payload.decode()))
    tag_success = parsed_json[0]["success"]
    #print('success', tag_success)
    temp_data = {}
    if tag_success:
        tag_json = parsed_json
        tag_id = tag_json[0]['tagId']
        #print(tag_id)
        if tag_id == '27199':
            tag_x_1 = tag_json[0]['data']['coordinates']['x']
            tag_y_1 = tag_json[0]['data']['coordinates']['y']
            #print('tag temp x =', tag_x_1, 'tag temp y =', tag_y_1)

            # Send position to queue
            q.queue.clear()
            q.put(tag_x_1)
            q.put(tag_y_1)
            #print(q.get())
            #print(q.get())
        else:
            pass
            #print('other tag')


def on_message_2(client, userdata, msg):
    global tag_q

    #q = Queue(maxsize=2)
    #time.sleep(0.5)
    parsed_json = (json.loads(msg.payload.decode()))
    tag_success = parsed_json[0]["success"]
    #print('success', tag_success)
    temp_data = {}
    if tag_success:
        tag_json = parsed_json
        tag_id = tag_json[0]['tagId']
        #print(tag_id)
        if tag_id == '27263':
            tag_x_2 = tag_json[0]['data']['coordinates']['x']
            tag_y_2 = tag_json[0]['data']['coordinates']['y']
            #print('tag temp x2 =', tag_x_2, 'tag temp y2 =', tag_y_2)

            # Send position to queue
            tag_q.queue.clear()
            tag_q.put(tag_x_2)
            tag_q.put(tag_y_2)
            # print(tag_q.get())
            # print(tag_q.get())
        else:
            pass
            #print('other tag')



def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed to topic!")


def thread_mir(mir_q):
    #q = Queue()
    for _ in cycle((None,)):
        #q.queue.clear()
        mir = MiR()
        mir_x = mir.show_x()
        mir_y = mir.show_y()
        #q_mir_y.queue.clear()
        mir_q.put((mir_x))
        mir_q.put((mir_y))
        #print(mir_q.get())
        #print(mir_q.get())

        #print('position x =', mir_x, ', position y =', mir_y, end='\n')
        time.sleep(0.5)


def thread_tag_1():
    #global q
    client = mqtt.Client()
    # Set callbacks
    client.on_connect = on_connect
    client.on_message = on_message_1
    client.on_subscribe = on_subscribe
    client.connect(host, port=port)
    client.subscribe(topic)


    # works blocking, other, non-blocking, clients are available too.
    client.loop_forever()

def thread_tag_2():
    global tag_q
    tag_q = Queue()
    client = mqtt.Client()
    # Set callbacks
    client.on_connect = on_connect
    client.on_message = on_message_2
    client.on_subscribe = on_subscribe
    client.connect(host, port=port)
    client.subscribe(topic)


    # works blocking, other, non-blocking, clients are available too.
    client.loop_forever()



def thread_judge(mir_q):
    mir = MiR()
    temp_x = mir.show_x()
    temp_y = mir.show_y()
    #print('temp_x =', temp_x, ', temp_y =', temp_y)
    global q, tag_q
    for _ in cycle((None,)):
        time.sleep(0.05)
        mir_x = mir_q.get()
        mir_y = mir_q.get()
        tag_x_1 = q.get()
        tag_y_1 = q.get()

        tag_x_2 = tag_q.get()
        tag_y_2 = tag_q.get()


        # Set the zero point
        mir_x = mir_x - 42.4
        mir_y = mir_y - 21.9

        tag_x_1 = tag_x_1 / 100
        tag_y_1 = tag_y_1 / 100
        tag_x_1 = tag_x_1 + 2
        tag_y_1 = tag_y_1 - 4

        tag_x_2 = tag_x_2 / 100
        tag_y_2 = tag_y_2 / 100
        tag_x_2 = tag_x_2
        tag_y_2 = tag_y_2 - 4

        mir_x = mir_x * 10
        mir_y = mir_y * 10


        print('mir_x =', int(mir_x), 'mir_y =', int(mir_y))
        print('tag_x_1 =', int(tag_x_1), 'tag_y_1 =', int(tag_y_1))
        print('tag_x_2 =', int(tag_x_2), 'tag_y_2 =', int(tag_y_2))

        # Set Safety Zones
        distance_1 = (int(mir_x) - int(tag_x_1))**2 + (int(mir_y) - int(tag_y_1))**2
        distance_2 = (int(mir_x) - int(tag_x_2))**2 + (int(mir_y) - int(tag_y_2))**2
        print('distance_1 =', int(math.sqrt(distance_1)), '&', 'distance_2 =', int(math.sqrt(distance_2)))


        if (math.sqrt(distance_1) <= 17) or (math.sqrt(distance_2) <= 17):
            print('###################################################in Zone_1')
        elif (math.sqrt(distance_1) <= 22) or (math.sqrt(distance_2) <= 22):
            print('###################################################in Zone_2')
        elif (math.sqrt(distance_1) <= 27) or (math.sqrt(distance_2) <= 27):
            print('###################################################in Zone_3')
        else: print('###################################################Not in any Zone')




        if temp_x != mir_x and temp_y != mir_y:
            print('MiR is moving')
            if (math.sqrt(distance_1) <= 17) or (math.sqrt(distance_2) <= 17):
                # Put the velocity which is equal to 0.1，修改速度为0.15
                r = requests.put("http://192.168.100.51/api/v2.0.0/settings/2078", headers=headers2, json=body4)
                print(r.status_code)
                print('velocity: 0.15')

            elif (math.sqrt(distance_1) <= 22) or (math.sqrt(distance_1) <= 22):
                # Put the velocity which is equal to 0.25，修改速度为0.25
                r = requests.put("http://192.168.100.51/api/v2.0.0/settings/2078", headers=headers2, json=body3)
                print(r.status_code)
                #print(r.status_code, r.content)
                print('velocity: 0.25')

            elif (math.sqrt(distance_1) <= 27) or (math.sqrt(distance_2) <= 27):
                # Put the velocity which is equal to 0.5，修改速度为0.5
                r = requests.put("http://192.168.100.51/api/v2.0.0/settings/2078", headers=headers2, json=body2)
                print(r.status_code)
                print('velocity: 0.5')

            else:  # Put the velocity which is equal to 1.1
                r = requests.put("http://192.168.100.51/api/v2.0.0/settings/2078", headers=headers2, json=body1)
                print(r.status_code)
                print('velocity: 1.1')
        else:
            print('MiR is docking')
        temp_x = mir_x
        temp_y = mir_y
        print('temp_x changes to', int(temp_x), 'temp_y changes to', int(temp_y))
        # except Exception as e:
        #     print('error',e)



def main():
    mir_q = Queue()
    q = Queue()

    mir_thread = threading.Thread(target=thread_mir, args=(mir_q,))
    tag_1_thread = threading.Thread(target=thread_tag_1)
    tag_2_thread = threading.Thread(target=thread_tag_2)
    judge_thread = threading.Thread(target=thread_judge, args=(mir_q,))
    mir_thread.start()
    judge_thread.start()
    tag_1_thread.start()
    tag_2_thread.start()


if __name__ == '__main__':
    main()