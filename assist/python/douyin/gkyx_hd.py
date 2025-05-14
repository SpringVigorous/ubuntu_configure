import requests
import json
import os
import pandas as pd
import time

import requests
import sys

from pathlib import Path

root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )

from base import as_normal,logger_helper,UpdateTimeType,cur_date_str,remove_directories_and_files,merge_df,str2time,downloads_async,parallel_json_normalize,optimized_to_excel,optimized_read_excel,get_next_filename,ThreadPool,guid
import requests
from datetime import datetime
from collections.abc import Callable
from queue import Queue
from base  import ThreadTask
import threading


dest_dir=r"F:\worm_practice\gkyx\hd"

import requests

headers = {
    'authority': 'live-play.vzan.com',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9',
    'authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiI2MDQ4ODA4MDAiLCJuYmYiOjE3NDYwMDcyNjksImV4cCI6MTc0NjA1MDQ5OSwiaWF0IjoxNzQ2MDA3Mjk5LCJpc3MiOiJ2emFuIiwiYXVkIjoidnphbiJ9.YmyMWWGC0xtJj_bGzNwn4gQ47ZCQalciBw_x387mMcw',
    'buid': '9E53C6E18A15FC5272C157351AE20631',
    'content-type': 'application/json;charset=UTF-8',
    'origin': 'https://bxxxsevzb.xwcx6.com',
    'pageurl': 'https://bxxxsevzb.xwcx6.com/live/page/1478925452?v=1746007199000&jumpitd=1&shauid=Evcc232puSL2VXw08UkVQQ**',
    'referer': 'https://bxxxsevzb.xwcx6.com/',
    'sec-ch-ua': '"Not)A;Brand";v="24", "Chromium";v="116"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.97 Safari/537.36 SE 2.X MetaSr 1.0',
    'x-requested-with': 'XMLHttpRequest',
    'zbvz-userid': '9E53C6E18A15FC5272C157351AE20631',
}

params = {
    'tpid': 'C7CEBE60EC8C7EE279211A8D34049F71',
    'time': '2147483647',
    'pagesize': '12',
    'mode': 'desc',
    'loadNewCache': '1',
}

# response = requests.get('https://live-play.vzan.com/api/topic/topic_msg', params=params, headers=headers)


org_json_queque=Queue()
org_json_stop_event=threading.Event()





class SaveJsonTask(ThreadTask):
    def __init__(self, input_queue, output_queue=None, stop_event=None,out_stop_event=None):
        
        ThreadTask.__init__(self, input_queue, output_queue, stop_event,out_stop_event)


        
    def set_handle_func(self,func:callable):
        self.handle_func=func
    
    def _handle_data(self, item) -> None:
        data,file_name=item
        self._logger.update_target("输出文件",file_name)
        self._logger.update_time(state=UpdateTimeType.STAGE)
        self._logger.trace(f"开始",update_time_type=UpdateTimeType.STAGE)
        if self.handle_func:
            self.handle_func(data,file_name)
        self._logger.info("完成",update_time_type=UpdateTimeType.STAGE)

thread_cache=ThreadPool()
thread_cache.start()

class MessageInfo:
    def __init__(self, data=None):
        if data and isinstance(data,dict):
            self.from_dict(data)
        else:
            self.time:int=None
            self.speaktime:datetime=None
        
    def from_dict(self,data:dict):
        self.set_data(data.get("time"), data.get("speaktime")) 
    def set_data(self,time,speaktime:str):
        self.time = int(time)  # 话题ID
        self.speaktime = str2time(speaktime) if speaktime else None  # 消息时间

    @property
    def time_valid(self):
        return bool(self.time)
    
    @property
    def speaktime_valid(self):
        return bool(self.speaktime)


    def is_time_less(self,time:int|str):
        if self.time_valid and time :
            return self.time<int(time)
            
        return False
    
    def is_speaktime_less(self,time:str|datetime):
        if self.speaktime_valid and time:
            if isinstance(time,str):
                time=str2time(time)
            return self.speaktime<time
        return False
    
    def speaktime_str(self):
        if self.speaktime_valid :
            return self.speaktime.strftime("%Y-%m-%d %H:%M:%S")
        return ""
    
    def __str__(self) -> str:
        return f"当前time:{self.time},speaktime:{self.speaktime_str()}"

    









def get_data(cur_time:None,last_info:MessageInfo=None):
    if cur_time:
        params["time"]=str(cur_time)


    
    logger=logger_helper()
    
    data_lst=[]
    i=0 

    cur_info=None
    while True:
        try:
            logger.update_target(cur_info or params["time"],detail=f"第{i}次")
            logger.trace("开始",update_time_type=UpdateTimeType.STAGE)
            response = requests.get('https://live-play.vzan.com/api/topic/topic_msg', params=params, headers=headers,timeout=15)
            if response.status_code!=200:
                logger.info(f"失败",update_time_type=UpdateTimeType.STAGE)
                break
            org_data=response.json()
            
            data=org_data["dataObj"]
            if not data:
                logger.info(f"失败",f"接收到内容：{org_data}",update_time_type=UpdateTimeType.STAGE)
                break
            
            data=sorted(data,key=lambda x: x['time'])
            data_lst.append(data)
            if not data:
                logger.info(f"失败",update_time_type=UpdateTimeType.STAGE)
                break
            first_item=data[0]
            cur_info=MessageInfo(first_item)
            if last_info:
                if cur_info.is_time_less(last_info.time):
                    logger.info(f"成功",f"{cur_info.time}<={last_info.time}",update_time_type=UpdateTimeType.STAGE)
                    break

                if cur_info.is_speaktime_less(last_info.speaktime):
                    logger.info(f"成功",f"{last_info.speaktime_str}<={last_info.speaktime_str}",update_time_type=UpdateTimeType.STAGE)
                    break
            params["time"]=str(cur_info.time)
            i+=1
            logger.info(f"成功",update_time_type=UpdateTimeType.STEP)
            # time.sleep(1)
        except Exception as e:
            logger.info(f"失败",f"原因{e}",update_time_type=UpdateTimeType.STAGE)
            break

    data=[]
    for item in reversed(data_lst) :
        data.extend(item)
    logger.info(f"整理完毕",update_time_type=UpdateTimeType.STAGE)
    return data,cur_info

def merge_data():
    data_lst=[]
    for  file in os.listdir(dest_dir):
        if not file.endswith(".json"):
            continue
        
        with open(os.path.join(dest_dir,file),encoding="utf-8") as f:
            cur_data=json.load(f)
            data_lst.append( cur_data["dataObj"])
    data=[]   
    for item in reversed(data_lst) :
        data.extend(item)
            
    return data

def merge_json_to_xlsx(file_name,each_count:int=None):
    data=[]
    logger=logger_helper(f"根据json文件合并",f"当前文件夹{dest_dir}")

    for  file in os.listdir(dest_dir):
        if not file.endswith(".json"):
            continue
        cur_json_file=os.path.join(dest_dir,file)
        logger.trace(f"正在读取{file}",update_time_type=UpdateTimeType.STEP)
        with open(cur_json_file,encoding="utf-8") as f:
            cur_data=json.load(f)
            data.extend( cur_data)
            logger.trace(f"读取完成,当前合计{len(cur_data)}条",update_time_type=UpdateTimeType.STEP)
    logger.info(f"读取完毕",update_time_type=UpdateTimeType.STAGE)
    
    cur_index=0
    def cur_file_name():
            return f"{file_name}_{cur_index:04}"
    if each_count:
        logger.info(f"开始导出,每个文件{each_count}条",update_time_type=UpdateTimeType.STAGE)
        for i in range(0,len(data),each_count):
            start_index=i*each_count
            end_index=min((i+1)*each_count,len(data))
            cur_file=cur_file_name()
            logger.stack_target(detail=cur_file)
            logger.info(f"开始导出",f"合计{end_index-start_index}条",update_time_type=UpdateTimeType.STEP)
            export_to_xlsx(data[:each_count],cur_file)
            logger.info(f"成功导出",update_time_type=UpdateTimeType.STAGE)
            data=data[each_count:]
            cur_index+=1
            logger.pop_target()
    elif data:
        cur_file=file_name
        logger.stack_target(detail=cur_file)
        logger.info(f"开始导出",f"合计{len(data)}条",update_time_type=UpdateTimeType.STEP)
        export_to_xlsx(data,cur_file)
        logger.info(f"成功导出",update_time_type=UpdateTimeType.STAGE)
        logger.pop_target()
    logger.info(f"合并完成",update_time_type=UpdateTimeType.STAGE)
    
    return True

def save_json_data(data,file_name):
    file_path=Path(os.path.join(dest_dir, f"{file_name}.json"))
    while os.path.exists(file_path): 
        file_path=file_path.with_stem(f"{file_name}_{guid()}")
    
    with open(str(file_path), "w", encoding="utf-8") as f:
        json.dump(data,f)
    
def load_json_data(file_name):
    # 使用with语句打开名为"response.json"的文件，以读取模式("r")和UTF-8编码
    with open(os.path.join(dest_dir, f"{file_name}.json"), "r", encoding="utf-8") as f:
        # 使用json模块的load函数从文件中加载JSON数据
        data=json.load(f)
    # 返回加载的JSON数据
    return data
def export_to_xlsx(data:list,file_name):
    logger=logger_helper("数据导出","转换为DataFrame")
    
    logger.trace("开始",update_time_type=UpdateTimeType.STEP)
    df=parallel_json_normalize(data, max_level=10,errors="ignore")
    logger.info("完成",update_time_type=UpdateTimeType.STEP)
    
    #替换掉换行符
    df["content"]=df["content"].apply(lambda x: x.replace("\n",";"))
    
    df.drop_duplicates(subset=["time"], inplace=True)
    df.sort_values(by="time",ascending=True, inplace=True)
    
    logger.update_target(detail="导出xlsx")
    logger.trace("开始",update_time_type=UpdateTimeType.STEP)
    
    thread_cache.submit(optimized_to_excel,df,os.path.join(dest_dir, f"{file_name}.xlsx"))
    
    # optimized_to_excel(df,os.path.join(dest_dir, f"{file_name}.xlsx"))
    logger.info("完成",update_time_type=UpdateTimeType.STEP)


    #输出到上一层的 json中
    
    def cache_json():
        with open(os.path.abspath(os.path.join(dest_dir, f"../json/{file_name}.json")),"w",encoding="utf-8") as f:
            df.to_json(f,orient="records",force_ascii=False)
            
    thread_cache.submit(cache_json)





# save_json_thread=SaveJsonTask(org_json_queque,stop_event=org_json_stop_event)
# save_json_thread.set_handle_func(save_json_data)
# save_json_thread.start()
def handle_message(file_name,cur_time=None,last_message:MessageInfo=None):
    data,cur_info=get_data(cur_time,last_message)
    if not data:
        return None
    logger=logger_helper("加入json输出队列",file_name)
    
    # org_json_queque.put((data,file_name))
    
    thread_cache.submit(save_json_data,data,file_name)
    
    # save_json_data(data,file_name)
    logger.info(f"成功",update_time_type=UpdateTimeType.STAGE)
    
    # data=merge_data()
    
    # data=load_data()

    # df=pd.json_normalize(data, max_level=10,errors="ignore")
    # df.to_excel(os.path.join(dest_dir, f"{file_name}.xlsx"))
    return cur_info




def loop_get_data(file_name,count:int,start_index:int=1,last_message:MessageInfo=None):
    cur_time=params["time"]
    logger=logger_helper(file_name)
    infos=[]
    def half_pagesize():
        count=int(int(params["pagesize"])/2)
        params["pagesize"]=str(count)
        logger.info("获取数量减半",f"目前{count}个")
        return count

    for i in range(start_index,count):

        cur_name=f"{file_name}_{i:04}"
        logger.update_target(detail=cur_name)
        logger.info("开始",cur_time,update_time_type=UpdateTimeType.STEP)
        cur_info=handle_message(cur_name,cur_time,last_message)
        if not cur_info:
            logger.info("结束",f"累计{i-1}次",update_time_type=UpdateTimeType.STAGE)
            if half_pagesize()<10:
                break
            else:
                continue
        else:
            logger.trace("成功",update_time_type=UpdateTimeType.STEP)
            infos.append(cur_info)
         
        cur_info=infos[-1]
        if last_message:
            if cur_info.is_time_less(last_message.time) or cur_info.is_speaktime_less(last_message.speaktime):
                logger.info("结束",f"累计{i}次",update_time_type=UpdateTimeType.STAGE)
                break    
        
        cur_time=cur_info.time
    logger.info("采集完成",update_time_type=UpdateTimeType.ALL)
            
        
def init_param(time_val:int=None,page_size:int=2000,tpid:str=None):
    if time_val:
        params["time"]=str(time_val)
    params["pagesize"]=str(page_size)
    if tpid:
        params["tpid"]=tpid
    pass     
    

def merge_xlsx():
    
    logger=logger_helper("合并xlxs文件",dest_dir)
    
    df_lst=[]
    for  file in os.listdir(dest_dir):
        if not file.endswith(".xlsx"):
            continue
        cur_file=os.path.join(dest_dir,file)

        logger.stack_target(detail=file)
        logger.trace(f"正在读取",update_time_type=UpdateTimeType.STEP)
        df=pd.read_excel(cur_file)
        logger.trace(f"读取成功",update_time_type=UpdateTimeType.STAGE)
        if not df.empty:
            df_lst.append(df)
        logger.pop_target()
        
    df=pd.concat(df_lst,axis=0,ignore_index=True)
    df.drop_duplicates(subset=["time"], inplace=True)
    df.sort_values(by="time",ascending=True, inplace=True)
    dest_file=os.path.join(dest_dir, f"{cur_date_str()}_合并.xlsx")
    
    logger.stack_target(detail=dest_file)
    logger.trace(f"开始写入",update_time_type=UpdateTimeType.STAGE)
    
    df.to_excel(dest_file)
    logger.trace(f"成功写入",update_time_type=UpdateTimeType.STAGE)
    
    logger.pop_target()
    logger.info(f"合并完成",update_time_type=UpdateTimeType.ALL)
async def download_images():
    
    json_path=os.path.join(dest_dir,"image.json")
    xlsx_path=os.path.join(dest_dir,"20250408_2.xlsx")
    logger=logger_helper("下载图片",xlsx_path)
    df=None
    if not os.path.exists(json_path):
        logger.info(f"读取开始",update_time_type=UpdateTimeType.STAGE)
        df=pd.read_excel(xlsx_path)
        logger.info(f"读取完成",update_time_type=UpdateTimeType.STAGE)
        
        df1=df[["userinfo.headimgurl","userinfo.userid"]].rename(columns={"userinfo.headimgurl":"url","userinfo.userid":"id"})
        df2=df[["tuser.headimgurl","tuser.id"]].rename(columns={"tuser.headimgurl":"url","tuser.id":"id"})
        
        df=pd.concat([df1,df2],axis=0,ignore_index=True)
        df.dropna(subset=["url"], inplace=True)
        df.drop_duplicates(subset=["id"], inplace=True)
        df["id"]=df["id"].astype(int)
        df.to_json(os.path.join(dest_dir,"image.json"),orient="records",force_ascii=False)
    else:
        df=pd.read_json(json_path)
    
        
    urls=[]
    files=[]
    for index,row in df.iterrows():
        url=row["url"]
        id=int(row["id"])
        file=os.path.join(dest_dir,"image",f"{id}.jpg")
        if os.path.exists(file):
            continue
        urls.append(url)
        files.append(file)


    logger.info(f"开始下载{len(urls)}个文件",update_time_type=UpdateTimeType.STAGE)
    await downloads_async(urls,files)
    logger.info(f"下载完成",update_time_type=UpdateTimeType.STAGE)

    logger.info(f"完成",update_time_type=UpdateTimeType.ALL)
    

def read_xlsx():
    file_path=Path(os.path.join(dest_dir,"20250420_1.xlsx"))
    df=optimized_read_excel(os.path.join(dest_dir,"20250420_1.xlsx"),usecols=["content"])
    return df


    
def find_result(df:pd.DataFrame):
    
    result = df[df['content'].str.contains('肾', na=False)]['content'].tolist()
    with open(os.path.join(dest_dir,"20250420_1.txt"),"w",encoding="utf-8") as f:
        f.write("\n".join(filter(lambda x: bool(x),result)))


def convert_xlsx_to_json():
    
    for  file in os.listdir(dest_dir):
        if not file.endswith(".xlsx"):
            continue
        cur_file=os.path.join(dest_dir,file)
        json_path=os.path.abspath(os.path.join(dest_dir,f"../json/{Path(cur_file).stem}.json"))
        df=pd.read_excel(cur_file)
        with open(json_path,"w",encoding="utf-8") as f:
            df.to_json(f,orient="records",force_ascii=False)

def main():
        
    file_name=get_next_filename(dest_dir,cur_date_str(),"xlsx")
    if not file_name:
        return
    
    file_name=Path(file_name).stem
    
    
    
    # asyncio.run(download_images()) 
    # exit()
    
    # init_param(time_val=504808846)
    init_param()

    logger=logger_helper("获取评论信息",file_name)
    
    input_params={"params":params,"headers":headers}
    logger.info("开始",f"参数：\n{json.dumps(input_params,ensure_ascii=False,indent=4 )}\n")
    last_message:MessageInfo=None
    #2025-04-08 16:11:58

    last_message:MessageInfo=MessageInfo({"time":455781213,"speaktime":"2025-04-26 18:08:27"})
    logger.info(f"获取开始",update_time_type=UpdateTimeType.STAGE)
    loop_get_data(file_name,1000,1,last_message)
    org_json_stop_event.set()
    # save_json_thread.join()
    thread_cache.join()
    
    thread_cache.restart()
    
    logger.info(f"获取结束",update_time_type=UpdateTimeType.STAGE)

    merge_json_to_xlsx(file_name)
    thread_cache.join()
    
    logger.info(f"整理到excel",update_time_type=UpdateTimeType.STAGE)
    
    remove_directories_and_files(dest_dir,posix_filter=[".json"])
    logger.info("完成",update_time_type=UpdateTimeType.ALL)
    # merge_xlsx()
if __name__=="__main__":
    main()
    

    
    
    
    # df=read_xlsx()
    # find_result(df)
    # convert_xlsx_to_json()
    # os.system(f"shutdown /s /t 1")