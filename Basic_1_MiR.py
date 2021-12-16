# 开发时间: 2021-09-22 13:48
import requests, json
import math
import time
class MiR():
    def __init__(self):
        self.host = "http://192.168.100.51/api/v2.0.0/"
        self.headers = {}
        self.headers['Content-Type'] = 'application/json'
        self.headers['Accept-Language'] = 'en_US'
        # self.headers[
        #     'Authorization'] = 'Basic RGlzdHJpYnV0b3I6NjJmMmYwZjFlZmYxMGQzMTUyYzk1ZjZmMDU5NjU3NmU0ODJiYjhlNDQ4MDY0MzNmNGNmOTI5NzkyODM0YjAxNA=='
        self.headers[
            'Authorization'] = 'Basic RGlzdHJpYnV0b3I6ZTNiMGM0NDI5OGZjMWMxNDlhZmJmNGM4OTk2ZmI5MjQyN2FlNDFlNDY0OWI5MzRjYTQ5NTk5MWI3ODUyYjg1NQ=='
        self.group_id = 'mirconst-guid-0000-0004-users0000000'
        # self.headers[
        #     'Authorization'] = 'Basic YWRtaW46OGM2OTc2ZTViNTQxMDQxNWJkZTkwOGJkNGRlZTE1ZGZiMTY3YTljODczZmM0YmI4YTgxZjZmMmFiNDQ4YTkxOA=='
        # self.group_id = 'mirconst-guid-0000-0011-missiongroup'
        # self.session_id = 'a2f5b1e6-d558-11ea-a95c-0001299f04e5'
    # get the system information
    def get_system_info(self):
        try:
            result = requests.get(self.host + 'status', headers=self.headers)
        except:
            return 'No Connection'
        return result.json()

    '''def get_system_info(self):
        try:
            result = requests.put(self.host + 'status', headers=self.headers)
        except:
            return 'No Connection'
        return result.json()'''
mir = MiR()
result = mir.get_system_info()
# result = mir.get_mission_guid("acti"
print(result)
