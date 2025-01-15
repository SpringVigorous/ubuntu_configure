# https://cgateway.bjmantis.net.cn/micor-live-guest/tenc/live/im/groupMsgList
import json
import requests
import os
import pandas as pd

import json
from datetime import datetime


import abc
import sys
from pathlib import Path


root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )
from base import exception_decorator,logger_helper,except_stack,normal_path,fetch_sync,decrypt_aes_128,get_folder_path,UpdateTimeType


import tkinter as tk
from tkinter import messagebox

def confirm_overwrite(file_name):
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    # 弹出确认对话框
    response = messagebox.askyesno("确认覆盖", f"文件 {file_name} 已存在，是否覆盖？")
    return response


# 秒时间戳 格式化
def convert_seconds_to_datetime(seconds):
    # 将秒时间戳转换为 datetime 对象
    dt = datetime.fromtimestamp(seconds)
    formatted_date = dt.strftime('%Y-%m-%d %H:%M:%S')
    
    return formatted_date
def handle_payload_extension(item:dict):
    if not "payload" in item:
        return
    payload=item["payload"]
    if "extension" in payload:
        raw_str=payload["extension"]
        if isinstance(raw_str,str):
            try:
                extension= json.loads(raw_str)
                payload["extension"]=extension
            except:
                pass


def handle_time(data:dict):
    if "time" in data:
        org_time=data["time"]
        data["time"]=convert_seconds_to_datetime(org_time)
        return org_time
        
        
def handle_raw_data(org_str):
    org_data=json.loads(org_str)

    data=org_data["data"]
    if not data:
        return None,0
    last_time=0
    
    dest=None
    
    if "list" in data:
        lst=data["list"]
        for item in lst:
            handle_payload_extension(item)
        dest=lst
    elif isinstance(data,list):
        for item in data:
            handle_payload_extension(item)
            last_time=handle_time(item)
        dest=data
    return dest,last_time


class MsgBase(metaclass=abc.ABCMeta):
       
    def __init__(self,msg_json_path:str) -> None:
        self.msg_json_path=msg_json_path
        self.logger=logger_helper(self.__class__.__name__,msg_json_path)
        pass
    
    def get_data(self,msg_json_name)->list:
        #从本地获取
        data=self.load_msg_json(msg_json_name)
        if data:
            return data

        #网上获取
        data=self.get_data_imp(msg_json_name)
        
        #保存到本地
        self.save_msg_json(msg_json_name,data)
        return data
    
    
    @abc.abstractmethod
    def get_data_imp(self,msg_json_name)->list:
        
        return []
     
    def load_msg_json(self,msg_json_name):
        data=None
        raw_json_path=self.real_path(msg_json_name)
        if os.path.exists(raw_json_path):
            with open(raw_json_path, "r", encoding="utf-8") as f:
                data= json.load(f)

        self.logger.info("成功" if data else "失败",f"【读取文件】{raw_json_path}")
            
            
        return data
     
    def save_msg_json(self,msg_json_name,data):
        
        if not data :
            return
        
        raw_json_path=self.real_path(msg_json_name)
        with open(raw_json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        self.logger.info("成功",f"【写入文件】{raw_json_path}")
    @property
    def msg_dir(self):
        return os.path.dirname(self.msg_json_path)
    
    
    @property
    def prefix_name(self):
        return os.path.basename(self.msg_json_path).split(".")[0]
            
    def handle_data(self,datas:list):
        if not datas:
            return
        self.logger.info("成功",f"记录个数:{len(datas)}")
        

        df_all=pd.json_normalize(datas)
        # df_all.sort_values(by="time",inplace=True)
        # df_all.drop(columns=["time"],inplace=True)
        
        all_xls_path=self.real_path("ai_msg_all.xlsx")
        if os.path.exists(all_xls_path):
            # 示例调用
            if not confirm_overwrite(all_xls_path):
                return
        df_all.to_excel(all_xls_path ,index=False)
        
        pass

    def real_path(self,file_name):
        if os.path.normpath(file_name)==os.path.normpath(self.msg_json_path):
            return self.msg_json_path
        
        
        return os.path.join(self.msg_dir,f"{self.prefix_name}_{file_name}")


    def handle(self):
        datas=self.get_data(self.msg_json_path)
        self.handle_data(datas)
        pass
    
class AIMsg(MsgBase):
    
    def __init__(self, msg_json_path: str) -> None:
        super().__init__(msg_json_path)
    def get_data_imp(self,msg_json_name):




        headers = {
            'authority': 'cgateway.bjmantis.net.cn',
            'sec-ch-ua': '";Not A Brand";v="99", "Chromium";v="94"',
            'csign': 'eea4af67e3ae0267ad8bc19318f255f5',
            'x-authorizationaccess': 'Bearer 60b2199ecc224e9cae6617f49f4def77',
            'sec-ch-ua-mobile': '?1',
            'authorization': 'Bearer eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJ7XCJjb21wYW55SWRcIjo4MDk3NixcIm9wZW5JZFwiOlwib2czVmw2YzkweVV6dGtLbUF6VzNaWE40SG1ZOFwiLFwidW5pb25JZFwiOlwib1NCRGo2dTdxU21manUtRm5fSC1tUDUzNGpvRVwifSIsImlhdCI6MTczNjk0ODcwNCwiZXhwIjoxNzM3ODU0MTA0fQ.BJ5KTQZxILSHWvfXG6AnI4e2dbNHfATxn097YB-sa7OVC94mbXPcWoGmeoSdhEcNsdmmmaJPAlp3ZWKI5Ka-RkRQwj2ftKm_0BN6FkER4vzvVjr1k9VrrXUFo-dZ8Si_zGZdg6kFgMTvxsyZ4_P6fHQYkesI-J80e8QqxsipG7h-hYHfhpEWrsJtdSOUo7CxUZSNVBhM7M2vSby2tF4zCpKCwaY__udNKDaI5xXu1oSX6R-j_AZHUNTi_05UJJ21eyjoNcCp2PYUeknfn94oYnJmrBFek2xc11h97oECEjX8_RadtByUM6gbGMJOW94waE4Evm7PfNZBu0wF8Ljmow',
            # Already added when you pass json=
            # 'content-type': 'application/json',
            'accept': 'application/json, text/plain, */*',
            'timestamp': '1736948754372',
            'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Mobile Safari/537.36',
            'uuid': '80976=bf6461899d7f4aee94d3b5c4a5082acc=064a4b5853e80b320591a3f3463597c7',
            'cid': '80976',
            'sec-ch-ua-platform': '"Android"',
            'origin': 'https://scrm.xuehaoke.com.cn',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://scrm.xuehaoke.com.cn/',
            'accept-language': 'zh-CN,zh;q=0.9',
        }

        json_data = {
            'companyId': '80976',
            'liveId': '689',
            'size': 200,
            'startTime': 1736940003,
        }




        # response = requests.post('https://cgateway.bjmantis.net.cn/micor-live-guest/tenc/live/im/getLiveImEsList', headers=headers, json=json_data)
        url='https://cgateway.bjmantis.net.cn/micor-live-guest/tenc/live/im/getLiveImEsList'


        # headers = {
        #     'authority': 'cgateway.bjmantis.net.cn',
        #     'sec-ch-ua': '";Not A Brand";v="99", "Chromium";v="94"',
        #     'csign': '0976b0d13206eab92e495fdb03eb125d',
        #     'x-authorizationaccess': 'Bearer 3efc815026534a4f980b8efc1abe240a',
        #     'sec-ch-ua-mobile': '?1',
        #     'authorization': 'Bearer eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJ7XCJjb21wYW55SWRcIjo4MDk3NixcIm9wZW5JZFwiOlwib2czVmw2YzkweVV6dGtLbUF6VzNaWE40SG1ZOFwiLFwidW5pb25JZFwiOlwib1NCRGo2dTdxU21manUtRm5fSC1tUDUzNGpvRVwifSIsImlhdCI6MTczNjg2MjAyOSwiZXhwIjoxNzM3NzY3NDI5fQ.mG-7HBFwKrTNM6Grdc4TR8IPmZ9T_u_5GnXjCUdAuKbkw_O8dqrrHcLndPf2yKTUGhyEJiRZfLZM46rmgl166aX6srXgygG4cX7ax4NMBnbKuv7je4jjJ_Vvtdk9OatfOeXdGifBTp02NLxhCCvpzgdzJjUEprVSnEn4e43Ibbq0dYKDU5L9M28rm8Z6kEWTOozzPhtWrbn2b3DIefw5uV3dClrjGhAqiLKDmWCw7BhGDzJJUu4q8qMSHqpFrNEM1cWYEHWqLGIngZ3z2yW-qJMVfWAvLksz02qQx5sskFewpaaqjt5_lzlCj315hFpRWrx-gAXu7unOQdvgAU3SZg',
        #     # Already added when you pass json=
        #     # 'content-type': 'application/json',
        #     'accept': 'application/json, text/plain, */*',
        #     'timestamp': '1736862256285',
        #     'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Mobile Safari/537.36',
        #     'uuid': '80976=bf6461899d7f4aee94d3b5c4a5082acc=064a4b5853e80b320591a3f3463597c7',
        #     'cid': '80976',
        #     'sec-ch-ua-platform': '"Android"',
        #     'origin': 'https://scrm.xuehaoke.com.cn',
        #     'sec-fetch-site': 'cross-site',
        #     'sec-fetch-mode': 'cors',
        #     'sec-fetch-dest': 'empty',
        #     'referer': 'https://scrm.xuehaoke.com.cn/',
        #     'accept-language': 'zh-CN,zh;q=0.9',
        # }

        # json_data = {
        #     'liveId': 688,
        #     'playback': 'Y',
        #     'page': 1,
        #     'pageSize': 20,
        # }


        
        # url='https://cgateway.bjmantis.net.cn/micor-live-guest/tenc/live/im/groupMsgList'


        i=1
        next_time=0
        mgs_lst=[]
        
        while True:
            headers['timestamp'] = str(int(datetime.now().timestamp()*1000))
            
            if i>1:
                json_data['startTime']=next_time
            
            json_data["page"]=i
            
            response = requests.post(url, headers=headers, json=json_data)
            if response.status_code!=200:
                break
            
            
            raw_data,last_time=handle_raw_data(response.text)
            if not raw_data:
                break
            self.logger.trace("成功",f"第{i}次请求\nurl:{url}\nheader:{headers}\njson:{json_data}\ncount:{len(raw_data)}")
            
            if not raw_data:
                break
            next_time=last_time+1
            mgs_lst.extend(raw_data)
            i+=1
        

        return mgs_lst

    
class JuNengMsg(MsgBase):
    
    def __init__(self, msg_json_path: str) -> None:
        super().__init__(msg_json_path)
    def get_data_imp(self,msg_json_name):



        cookies = {
            'appName': 'zhxbjxxkjfwh',
            'zhxbjxxkjfwh_live_global_cfg': '%7B%22v%22%3A1%2C%22app_id%22%3A%22wx5263a20f794a5230%22%2C%22app_name%22%3A%22zhxbjxxkjfwh%22%2C%22app_title%22%3A%22%E8%81%9A%E9%87%8F%E7%9F%AD%E5%89%A7-%E5%90%B8%E5%BC%95%E5%8A%9B%22%2C%22logo%22%3A%22http%3A%2F%2Fimg.lesimao.net%2Ff1bc09e8aae5b7fc07e08403da57c868_1.jpg%22%2C%22ali_log%22%3A%7B%22project%22%3A%22pageview%22%2C%22logstore%22%3A%22pageview%22%2C%22endpoint%22%3A%22cn-beijing.log.aliyuncs.com%22%7D%2C%22log_cfg%22%3A%7B%22adtracksyspage%22%3A%22adtracksyspage%22%2C%22livetm%22%3A%22livetm%22%2C%22liveact%22%3A%22liveact%22%2C%22livesyslog%22%3A%22livesyslog%22%2C%22redvideotm%22%3A%22redvideotm%22%7D%7D',
            'zhxbjxxkjfwh_user_id': '59648347',
            'zhxbjxxkjfwh_cipher': '52e7b96909f2396c05cc08cf3557acf5',
            'zhxbjxxkjfwh_login_code': '1382990353',
            'p_h5_u': 'C018DD26-6B6C-426E-AD60-FE68F655EB58',
            'OUTFOX_SEARCH_USER_ID_NCOO': '1525835353.5591333',
            '___rl__test__cookies': '1736843982747',
        }

        headers = {
            'Connection': 'keep-alive',
            'sec-ch-ua': '";Not A Brand";v="99", "Chromium";v="94"',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/x-www-form-urlencoded',
            'sec-ch-ua-mobile': '?1',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Mobile Safari/537.36',
            'sec-ch-ua-platform': '"Android"',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://e.zhenhaoxue.top/Live_Replay?appname=zhxbjxxkjfwh&course_id=11342&period_id=146795&room_id=5062d1b&rdn=76138485&sale_id=9050',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            # Requests sorts cookies= alphabetically
            # 'Cookie': 'appName=zhxbjxxkjfwh; zhxbjxxkjfwh_live_global_cfg=%7B%22v%22%3A1%2C%22app_id%22%3A%22wx5263a20f794a5230%22%2C%22app_name%22%3A%22zhxbjxxkjfwh%22%2C%22app_title%22%3A%22%E8%81%9A%E9%87%8F%E7%9F%AD%E5%89%A7-%E5%90%B8%E5%BC%95%E5%8A%9B%22%2C%22logo%22%3A%22http%3A%2F%2Fimg.lesimao.net%2Ff1bc09e8aae5b7fc07e08403da57c868_1.jpg%22%2C%22ali_log%22%3A%7B%22project%22%3A%22pageview%22%2C%22logstore%22%3A%22pageview%22%2C%22endpoint%22%3A%22cn-beijing.log.aliyuncs.com%22%7D%2C%22log_cfg%22%3A%7B%22adtracksyspage%22%3A%22adtracksyspage%22%2C%22livetm%22%3A%22livetm%22%2C%22liveact%22%3A%22liveact%22%2C%22livesyslog%22%3A%22livesyslog%22%2C%22redvideotm%22%3A%22redvideotm%22%7D%7D; zhxbjxxkjfwh_user_id=59648347; zhxbjxxkjfwh_cipher=52e7b96909f2396c05cc08cf3557acf5; zhxbjxxkjfwh_login_code=1382990353; p_h5_u=C018DD26-6B6C-426E-AD60-FE68F655EB58; OUTFOX_SEARCH_USER_ID_NCOO=1525835353.5591333; ___rl__test__cookies=1736843982747',
        }

        params = {
            'course_id': '11342',
            'period_id': '146795',
            'room_id': '5062d1b',
            'user_id': '59648347',
            'appname': 'zhxbjxxkjfwh',
            'reqtoken': '2321d4b015e453d795029bd1abd3281b',
        }




        response = requests.get('https://e.zhenhaoxue.top/V1_LiveRoom_LiveRoom/GetAllChatList/', params=params, cookies=cookies, headers=headers)

        raw_data=handle_raw_data(response.content)
        
        
        return raw_data[0]["list"]


    
class HuoReMsg(MsgBase):
    
    def __init__(self, msg_json_path: str) -> None:
        super().__init__(msg_json_path)
    def get_data_imp(self,msg_json_name):
        headers = {
            'authority': 'cgateway.bjmantis.net.cn',
            'sec-ch-ua': '";Not A Brand";v="99", "Chromium";v="94"',
            'csign': 'be7f499f2df0a0a9e0eaf92f40a312c3',
            'x-authorizationaccess': 'Bearer ea056b0ac91741b18e5a5af7a4c6433c',
            'sec-ch-ua-mobile': '?1',
            'authorization': 'Bearer eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJ7XCJjb21wYW55SWRcIjo4MTAzNSxcIm9wZW5JZFwiOlwib3A5WGQ2MW01MUJaSmpVaUNBSVktYnNxVjFzQVwiLFwidW5pb25JZFwiOlwibzlaWk02c3kycTNZX01XUXZ2NDNfZWJFY0NmOFwifSIsImlhdCI6MTczNjc1OTkyMywiZXhwIjoxNzM3MzcwMTIzfQ.mjHFmfQRD6NKj2fMgzlNglWaUPfulzV2dyrV_5LNoaHJo7nCnw0iW-hVzf2pejwoXt9i1aCL39FMWd-8nGSyZWQBkqJxoAa9NAdAD1uthAtmHvTq3qOwMHLhN_3VhTz0dKzUan74Ih9xBpRBVxAp3XRMsTBuOuVukJkWQxgMdVGvqSJ2trT_TCt32djeMtZfi-76w0awmXcmoZ9j6doJV4TOQnCSf0iQVkjeOQKXHWNzFFvMELD8QE8tlyGSa74FCK50Pe-b27GX4QERkMU0LfifKn_HjlC85mD_QkCpkNodw4im0t2HyfeQM39UOzYtRIlv6ofl_si91Q1q4gjEqQ',
            # Already added when you pass json=
            # 'content-type': 'application/json',
            'accept': 'application/json, text/plain, */*',
            'timestamp': '1736759919953',
            'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Mobile Safari/537.36',
            'uuid': '81035=5dd5ef27f9454e948dec99db44a13753=ed237c3da9141c1b1f115c48c0fc2587',
            'cid': '81035',
            'sec-ch-ua-platform': '"Android"',
            'origin': 'https://81035.bjmantis2.net',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://81035.bjmantis2.net/',
            'accept-language': 'zh-CN,zh;q=0.9',
        }
        json_data = {
            'liveId': 780,
            'playback': 'Y',
            'page': 1,
            'pageSize': 20,
        }

        i=1
        org_lst=[]
        
        while True:
            raw_data={}
            
            json_data['page']=i
            response = requests.post('https://cgateway.bjmantis.net.cn/micor-live-guest/tenc/live/im/groupMsgList', headers=headers, json=json_data)
            if response.status_code!=200:
                break
            
            raw_data= handle_raw_data(response.content)

            #从临时文件读取
            # file_path=os.path.join(r"F:\test\ubuntu_configure\assist\python",f"msg{i}.json")
            # if  not os.path.exists(file_path):
            #     break
            # with open(file_path, "r", encoding="utf-8") as f:
            #     raw_data=json.load(f)
            
            
            org_lst.append(raw_data["data"]["list"])

            if raw_data["isLastPage"] :
                break
            i+=1
        

        lst=[ ]
        for item in reversed(org_lst):
            lst.extend(item)
        return lst


class TempMsg(MsgBase):
    
    def __init__(self, msg_json_path: str) -> None:
        super().__init__(msg_json_path)
    def get_data_imp(self,msg_json_name):


        # cookies = {
        #     'appName': 'zhxbjxxkjfwh',
        #     'zhxbjxxkjfwh_live_global_cfg': '%7B%22v%22%3A1%2C%22app_id%22%3A%22wx5263a20f794a5230%22%2C%22app_name%22%3A%22zhxbjxxkjfwh%22%2C%22app_title%22%3A%22%E8%81%9A%E9%87%8F%E7%9F%AD%E5%89%A7-%E5%90%B8%E5%BC%95%E5%8A%9B%22%2C%22logo%22%3A%22http%3A%2F%2Fimg.lesimao.net%2Ff1bc09e8aae5b7fc07e08403da57c868_1.jpg%22%2C%22ali_log%22%3A%7B%22project%22%3A%22pageview%22%2C%22logstore%22%3A%22pageview%22%2C%22endpoint%22%3A%22cn-beijing.log.aliyuncs.com%22%7D%2C%22log_cfg%22%3A%7B%22adtracksyspage%22%3A%22adtracksyspage%22%2C%22livetm%22%3A%22livetm%22%2C%22liveact%22%3A%22liveact%22%2C%22livesyslog%22%3A%22livesyslog%22%2C%22redvideotm%22%3A%22redvideotm%22%7D%7D',
        #     'zhxbjxxkjfwh_user_id': '59648347',
        #     'zhxbjxxkjfwh_cipher': '52e7b96909f2396c05cc08cf3557acf5',
        #     'zhxbjxxkjfwh_login_code': '1382990353',
        #     'p_h5_u': 'C018DD26-6B6C-426E-AD60-FE68F655EB58',
        #     'OUTFOX_SEARCH_USER_ID_NCOO': '1525835353.5591333',
        #     '___rl__test__cookies': '1736843982747',
        # }

        # headers = {
        #     'Connection': 'keep-alive',
        #     'sec-ch-ua': '";Not A Brand";v="99", "Chromium";v="94"',
        #     'Accept': 'application/json, text/plain, */*',
        #     'Content-Type': 'application/x-www-form-urlencoded',
        #     'sec-ch-ua-mobile': '?1',
        #     'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Mobile Safari/537.36',
        #     'sec-ch-ua-platform': '"Android"',
        #     'Sec-Fetch-Site': 'same-origin',
        #     'Sec-Fetch-Mode': 'cors',
        #     'Sec-Fetch-Dest': 'empty',
        #     'Referer': 'https://e.zhenhaoxue.top/Live_Replay?appname=zhxbjxxkjfwh&course_id=11342&period_id=146795&room_id=5062d1b&rdn=76138485&sale_id=9050',
        #     'Accept-Language': 'zh-CN,zh;q=0.9',
        #     # Requests sorts cookies= alphabetically
        #     # 'Cookie': 'appName=zhxbjxxkjfwh; zhxbjxxkjfwh_live_global_cfg=%7B%22v%22%3A1%2C%22app_id%22%3A%22wx5263a20f794a5230%22%2C%22app_name%22%3A%22zhxbjxxkjfwh%22%2C%22app_title%22%3A%22%E8%81%9A%E9%87%8F%E7%9F%AD%E5%89%A7-%E5%90%B8%E5%BC%95%E5%8A%9B%22%2C%22logo%22%3A%22http%3A%2F%2Fimg.lesimao.net%2Ff1bc09e8aae5b7fc07e08403da57c868_1.jpg%22%2C%22ali_log%22%3A%7B%22project%22%3A%22pageview%22%2C%22logstore%22%3A%22pageview%22%2C%22endpoint%22%3A%22cn-beijing.log.aliyuncs.com%22%7D%2C%22log_cfg%22%3A%7B%22adtracksyspage%22%3A%22adtracksyspage%22%2C%22livetm%22%3A%22livetm%22%2C%22liveact%22%3A%22liveact%22%2C%22livesyslog%22%3A%22livesyslog%22%2C%22redvideotm%22%3A%22redvideotm%22%7D%7D; zhxbjxxkjfwh_user_id=59648347; zhxbjxxkjfwh_cipher=52e7b96909f2396c05cc08cf3557acf5; zhxbjxxkjfwh_login_code=1382990353; p_h5_u=C018DD26-6B6C-426E-AD60-FE68F655EB58; OUTFOX_SEARCH_USER_ID_NCOO=1525835353.5591333; ___rl__test__cookies=1736843982747',
        # }

        # params = {
        #     'course_id': '11342',
        #     'period_id': '146795',
        #     'room_id': '5062d1b',
        #     'user_id': '59648347',
        #     'appname': 'zhxbjxxkjfwh',
        #     'reqtoken': '5a87240262c4698fe7b627b649a62d86',
        # }

        # response = requests.get('https://e.zhenhaoxue.top/V1_LiveRoom_LiveRoom/GetLiveRoomExtInfo/', params=params, cookies=cookies, headers=headers)
        
        


        cookies = {
            'appName': 'zhxbjxxkjfwh',
            'zhxbjxxkjfwh_live_global_cfg': '%7B%22v%22%3A1%2C%22app_id%22%3A%22wx5263a20f794a5230%22%2C%22app_name%22%3A%22zhxbjxxkjfwh%22%2C%22app_title%22%3A%22%E8%81%9A%E9%87%8F%E7%9F%AD%E5%89%A7-%E5%90%B8%E5%BC%95%E5%8A%9B%22%2C%22logo%22%3A%22http%3A%2F%2Fimg.lesimao.net%2Ff1bc09e8aae5b7fc07e08403da57c868_1.jpg%22%2C%22ali_log%22%3A%7B%22project%22%3A%22pageview%22%2C%22logstore%22%3A%22pageview%22%2C%22endpoint%22%3A%22cn-beijing.log.aliyuncs.com%22%7D%2C%22log_cfg%22%3A%7B%22adtracksyspage%22%3A%22adtracksyspage%22%2C%22livetm%22%3A%22livetm%22%2C%22liveact%22%3A%22liveact%22%2C%22livesyslog%22%3A%22livesyslog%22%2C%22redvideotm%22%3A%22redvideotm%22%7D%7D',
            'zhxbjxxkjfwh_user_id': '59648347',
            'zhxbjxxkjfwh_cipher': '52e7b96909f2396c05cc08cf3557acf5',
            'zhxbjxxkjfwh_login_code': '1382990353',
            'p_h5_u': 'C018DD26-6B6C-426E-AD60-FE68F655EB58',
            'OUTFOX_SEARCH_USER_ID_NCOO': '1525835353.5591333',
            '___rl__test__cookies': '1736843982747',
        }

        headers = {
            'Connection': 'keep-alive',
            'sec-ch-ua': '";Not A Brand";v="99", "Chromium";v="94"',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/x-www-form-urlencoded',
            'sec-ch-ua-mobile': '?1',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Mobile Safari/537.36',
            'sec-ch-ua-platform': '"Android"',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://e.zhenhaoxue.top/Live_Replay?appname=zhxbjxxkjfwh&course_id=11342&period_id=146795&room_id=5062d1b&rdn=76138485&sale_id=9050',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            # Requests sorts cookies= alphabetically
            # 'Cookie': 'appName=zhxbjxxkjfwh; zhxbjxxkjfwh_live_global_cfg=%7B%22v%22%3A1%2C%22app_id%22%3A%22wx5263a20f794a5230%22%2C%22app_name%22%3A%22zhxbjxxkjfwh%22%2C%22app_title%22%3A%22%E8%81%9A%E9%87%8F%E7%9F%AD%E5%89%A7-%E5%90%B8%E5%BC%95%E5%8A%9B%22%2C%22logo%22%3A%22http%3A%2F%2Fimg.lesimao.net%2Ff1bc09e8aae5b7fc07e08403da57c868_1.jpg%22%2C%22ali_log%22%3A%7B%22project%22%3A%22pageview%22%2C%22logstore%22%3A%22pageview%22%2C%22endpoint%22%3A%22cn-beijing.log.aliyuncs.com%22%7D%2C%22log_cfg%22%3A%7B%22adtracksyspage%22%3A%22adtracksyspage%22%2C%22livetm%22%3A%22livetm%22%2C%22liveact%22%3A%22liveact%22%2C%22livesyslog%22%3A%22livesyslog%22%2C%22redvideotm%22%3A%22redvideotm%22%7D%7D; zhxbjxxkjfwh_user_id=59648347; zhxbjxxkjfwh_cipher=52e7b96909f2396c05cc08cf3557acf5; zhxbjxxkjfwh_login_code=1382990353; p_h5_u=C018DD26-6B6C-426E-AD60-FE68F655EB58; OUTFOX_SEARCH_USER_ID_NCOO=1525835353.5591333; ___rl__test__cookies=1736843982747',
        }

        params = {
            'page': 'replay',
            'course_id': '11342',
            'period_id': '146795',
            'room_id': '5062d1b',
            'user_id': '59648347',
            'appname': 'zhxbjxxkjfwh',
            'obj_id': '',
            'obj_id_2': '',
            'reqtoken': '6f1dc05d95e15177975e59deec56c81e',
        }

        response = requests.get('https://e.zhenhaoxue.top/V1_LiveRoom_LiveRoom/GetLiveRoomInfo/', params=params, cookies=cookies, headers=headers)


        raw_data=handle_raw_data(response.content)
        
        with open(msg_json_name,encoding="utf-8",mode="w") as f:
            json.dump(raw_data,f,ensure_ascii=False,indent=4)
        
        return None


def handle_data(lst,name_prefix=""):

    name_prefix=name_prefix+"_" if name_prefix else ""
    
    #处理时间
    for item in lst:
        item["time"]=convert_seconds_to_datetime(item["time"])
    with open(f"{name_prefix}msg_all.json",encoding="utf-8",mode="w") as f:
        json.dump(lst,f,ensure_ascii=False,indent=4)    
    df_all=pd.json_normalize(lst)
    df_all.sort_values(by="time",inplace=True)
    # df_all.to_excel(f"{name_prefix}msg_all.xlsx",index=False)
        
    no_pay=df_all.loc[~df_all["payload.extension.followUserId"].isnull(),:]
    no_pay.to_excel(f"{name_prefix}msg_no_pay.xlsx",index=False)
    exit(0)
    
    extends=[]

    
    exit(0)
    
    df=pd.json_normalize(extends)
    students= df.loc[df["userType"]=="STUDENT",:]
    
    
    df.to_excel(f"{name_prefix}msg.xlsx",index=False)
    students.to_excel(f"{name_prefix}msg_students.xlsx",index=False)
    

if __name__=="__main__":
    # get_huoren("1.12")
   
    # print(convert_seconds_to_datetime(662800001))
    # exit(0)
   
    ai=AIMsg(r"F:\教程\短视频教程\ai好课\msg\3.json")
    ai.handle()

    # huore=HuoReMsg(r"F:\教程\短视频教程\火热短剧\msg\1.json")
    # huore.handle()
    
    # juneng=JuNengMsg(r"F:\教程\短视频教程\聚能短剧\msg\4.json")
    # juneng.handle()
    
    
    # temp=TempMsg(r"F:\教程\短视频教程\聚能短剧\msg\temp2.json")
    # temp.handle()