# 开发时间: 2021-11-19 11:25
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

headers2 = {'Content-Type': 'application/json',
            'id': '2078',
            'Accept-Language': 'en_US',
            'Authorization': 'Basic RGlzdHJpYnV0b3I6NjJmMmYwZjFlZmYxMGQzMTUyYzk1ZjZmMDU5NjU3NmU0ODJiYjhlNDQ4MDY0MzNmNGNmOTI5NzkyODM0YjAxNA=='}
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
            self.robot_orientation = robot_json['position']['orientation']
            # print('position x', self.robot_x, 'position y', self.robot_y, end='\n')
            # print(result)
        except:
            return 'No Connection'
        return result.json()

    def show_x(self):
        # self.x0 = x0
        self.get_system_info()
        # print(self.robot_x)
        return self.robot_x

    def show_y(self):
        # self.y0 = y0
        self.get_system_info()
        return self.robot_y

    def show_orientation(self):
        self.get_system_info()
        return self.robot_orientation


host = "172.27.15.23"  # fill in the IP of your gateway
port = 1883
topic = "tags"
client = mqtt.Client()
q = Queue()


def on_connect(client, userdata, flags, rc):
    print(mqtt.connack_string(rc))


def on_message(client, userdata, msg):
    global q
    parsed_json = (json.loads(msg.payload.decode()))
    tag_success = parsed_json[0]["success"]
    # print('success', tag_success)
    if tag_success:
        tag_json = parsed_json
        tag_id = tag_json[0]['tagId']
        # print(tag_id)
        if tag_id == '27199':
            tag_x = tag_json[0]['data']['coordinates']['x']
            tag_y = tag_json[0]['data']['coordinates']['y']
            # print('tag temp x =', tag_x, 'tag temp y =', tag_y)

            q.queue.clear()
            # Send position to queue
            q.put(tag_x)
            q.put(tag_y)
        else:
            pass
            # print('other tag')


def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed to topic!")


def thread_mir(mir_q):
    # q = Queue()
    for _ in cycle((None,)):
        # q.queue.clear()
        mir = MiR()
        mir_x = mir.show_x()
        mir_y = mir.show_y()

        mir_q.put((mir_x))
        mir_q.put((mir_y))

        # print('position x =', mir_x, ', position y =', mir_y, end='\n')
        time.sleep(0.5)


def thread_tag():
    client = mqtt.Client()
    # Set callbacks
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_subscribe = on_subscribe
    client.connect(host, port=port)
    client.subscribe(topic)

    # works blocking, other, non-blocking, clients are available too.
    client.loop_forever()


def thread_judge(mir_q):
    last_tag_x = 0
    last_tag_y = 0
    mir = MiR()
    temp_x = mir.show_x()
    temp_y = mir.show_y()
    print('temp_x =', temp_x, ', temp_y =', temp_y)
    global q, signal_q
    signal_q = Queue()
    i = 0
    for _ in cycle((None,)):
        α = mir.show_orientation()
        mir_x = mir_q.get()
        mir_y = mir_q.get()
        tag_x = q.get()
        tag_y = q.get()

        # Set the zero point
        mir_x = mir_x - 42.4
        mir_y = mir_y - 21.9
        tag_x = tag_x / 100
        tag_y = tag_y / 100
        tag_x = tag_x + 2
        mir_x = mir_x * 10
        mir_y = mir_y * 10

        # Calculate the orientation
        tan_β = (tag_y - mir_y) / (tag_x - mir_x)
        β = math.degrees(math.atan(tan_β))
        # Change to 360 degree
        if α < 0:
            α = α + 360
        if tag_x < mir_x:
            β = β + 180
        elif (tag_x > mir_x) and (tag_y < mir_y):
            β = β + 360
        print('α = ', int(α), 'β = ', int(β))
        # TAG_x= round(tag_x, 1)

        if i == 2:
            if (int(tag_x) == int(last_tag_x)) and (int(tag_x) > int(last_tag_x)):
                γ = 90
            elif (int(tag_x) == int(last_tag_x)) and (int(tag_x) < int(last_tag_x)):
                γ = -90
            elif (int(tag_x) == int(last_tag_x)) and (int(tag_y) == int(last_tag_y)):
                γ = 0
            else:
                tan_γ = (tag_y - last_tag_y) / (tag_x - last_tag_x)
                print(tan_γ)
                γ = math.degrees(math.atan(tan_γ))
                # Change to 360 degree
                if tag_x < last_tag_x:
                    γ = γ + 180
                elif (tag_x > last_tag_x) and (tag_y < last_tag_y):
                    γ = γ + 360
            print('γ = ', int(γ), 'last_tag_x =', last_tag_x, 'tag_x =', tag_x, 'last_tag_y =', last_tag_y, 'tag_y =',
                  tag_y)

        print('mir_x =', int(mir_x), 'mir_y =', int(mir_y))
        print('tag_x =', int(tag_x), 'tag_y =', int(tag_y))

        # Set Safety Zone
        distance = (int(mir_x) - int(tag_x)) ** 2 + (int(mir_y) - int(tag_y)) ** 2
        print('distance =', int(math.sqrt(distance)))


        if math.sqrt(distance) <= 17:
            print('################################################### In Zone_1')
        elif math.sqrt(distance) <= 22:
            print('################################################### In Zone_2')
        elif math.sqrt(distance) <= 27:
            print('################################################### In Zone_3')
        else:
            print('################################################### Not in any Zone')

        # Predictable Judge
        if i == 2:
            # i = 0
            signal_q.queue.clear()
            if ((int(α)-15) <= int(γ) <= (int(α)+15)) or ((int(α)+165) <= int(γ) <= (int(α)+195)) or ((int(α)-195) <= int(γ) <= (int(α)-165)):
                signal = True
            else:
                signal = False
            print('signal =', signal)
            signal_q.put(signal)
            if math.sqrt(distance) <= 100:
                print('################################################### In Predictable Zone')
            # else:
            #     print('################################################### Not in Predictable Zone')

                # 第一象限
                if 0 <= α < 90:
                    if (α < β < (α + 90)) and (0 <= γ < α):
                        print('There is a possibility of collision between human and MiR')
                    elif (α < β < (α + 90)) and ((180 + β) < γ <= 360):
                        print('There is a possibility of collision between human and MiR')
                    elif ((α + 270) < β <= 360) and (α < γ < (β - 180)):
                        print('There is a possibility of collision between human and MiR')
                    elif (0 <= β < α) and (α < γ < (180 + β)):
                        print('There is a possibility of collision between human and MiR')
                    else:
                        pass
                # 第二象限
                elif 90 <= α < 180:
                    #print('HELLO*****************8')
                    if (α < β < 180) and (0 < γ < α):
                        print('There is a possibility of collision between human and MiR')
                    elif (α < β < 180) and ((180 + β) < γ <= 360):
                        print('There is a possibility of collision between human and MiR')
                    elif (180 < β < (α + 90)) and ((β - 180) < γ <= α):
                        print('There is a possibility of collision between human and MiR')
                    elif ((α - 90) < β < α) and (α < γ < (180 + β)):
                        print('There is a possibility of collision between human and MiR')
                    else:
                        pass
                # 第三象限
                elif 180 <= α < 270:
                    if (α < β < (α + 90)) and ((β - 180) < γ < α):
                        print('There is a possibility of collision between human and MiR')
                    elif ((α - 90) < β < 180) and (α < γ < (180 + β)):
                        print('There is a possibility of collision between human and MiR')
                    elif (180 < β < α) and (α < γ < 360):
                        print('There is a possibility of collision between human and MiR')
                    elif (180 < β < α) and (0 < γ < (β - 180)):
                        print('There is a possibility of collision between human and MiR')
                    else:
                        pass
                # 第四象限
                elif 270 <= α < 360:
                    if (α < β <= 360) and ((β - 180) < γ < α):
                        print('There is a possibility of collision between human and MiR')
                    elif (0 <= β < (α - 270)) and ((β + 180) < γ < α):
                        print('There is a possibility of collision between human and MiR')
                    elif ((α - 90) < β < α) and (α < γ <= 360):
                        print('There is a possibility of collision between human and MiR')
                    elif ((α - 90) < β < α) and (0 <= γ < (β - 180)):
                        print('There is a possibility of collision between human and MiR')
                    else:
                        pass
                else:
                    print('################################################### Not in Predictable Zone')

        # sign = signal_q.get()
        if i == 2:
            i = 0
            sign = signal_q.get()
            print('sign =', sign)
        else:
            sign = False
        if temp_x != mir_x and temp_y != mir_y:
            print('MiR is moving')
            if sign == True:
                print('The human walking direction is parallel to the MiR moving direction')
            if sign == False:
                if math.sqrt(distance) <= 17:
                    # Put the velocity which is equal to 0.1，修改速度为0.15
                    r = requests.put("http://192.168.100.51/api/v2.0.0/settings/2078", headers=headers2, json=body4)
                    print(r.status_code)
                    print('Linear velocity: 0.15')

                elif math.sqrt(distance) <= 22:
                    # Put the velocity which is equal to 0.25，修改速度为0.25
                    r = requests.put("http://192.168.100.51/api/v2.0.0/settings/2078", headers=headers2, json=body3)
                    print(r.status_code)
                    print('Linear velocity: 0.25')

                elif math.sqrt(distance) <= 27:
                    # Put the velocity which is equal to 0.5，修改速度为0.5
                    r = requests.put("http://192.168.100.51/api/v2.0.0/settings/2078", headers=headers2, json=body2)
                    print(r.status_code)
                    print('Linear velocity: 0.5')

                else:  # Put the velocity which is equal to 1.1
                    r = requests.put("http://192.168.100.51/api/v2.0.0/settings/2078", headers=headers2, json=body1)
                    print(r.status_code)
                    print('Linear velocity: 1.1')
        else:
            print('MiR is docking')
        temp_x = mir_x
        temp_y = mir_y
        if i == 0:
            last_tag_x = tag_x
            last_tag_y = tag_y
        i += 1
        print('temp_x changes to', int(temp_x), 'temp_y changes to', int(temp_y), 'i = ', i)


def main():
    mir_q = Queue()
    q = Queue()
    mir_thread = threading.Thread(target=thread_mir, args=(mir_q,))
    tag_thread = threading.Thread(target=thread_tag)
    judge_thread = threading.Thread(target=thread_judge, args=(mir_q,))
    mir_thread.start()
    judge_thread.start()
    tag_thread.start()


if __name__ == '__main__':
    main()