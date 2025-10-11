import json
import re
import pandas as pd
import sys
import os
from pathlib import Path





from base.path_tools import get_all_files_pathlib


def url_data(json_path:str):
    try:
        with open(json_path,"r",encoding="utf-8") as f:
            data = json.load(f)
    except:
        with open(json_path,"r",encoding="utf-8-sig") as f:
            data = json.load(f)
    return data["url"],data["name"],data["hash"]

#lat_func:function(file_path)->dict|None
def dir_data(dir_path:str,filter_str:str,lat_func):
    paths=get_all_files_pathlib(dir_path,[filter_str])
    lst=[]
    for file_path in paths:
        data=lat_func(file_path)
        if data:
            lst.append(data)
    return pd.json_normalize(lst)
 

def dir_url_datas(dir_path:str)->pd.DataFrame:
    
    def lat_func(file_path):
        cur_path=Path(file_path)
        if "-lost" in cur_path.name:
            return None
        url,name,hash=url_data(file_path)
        return {"url":url,"name":name,"hash":hash,"url_path":file_path}
    
    return dir_data(dir_path,".json",lat_func)
def dir_video_datas(dir_path:str):
    def lat_func(file_path):
        cur_path=Path(file_path)
        return {"name":cur_path.stem,"mp4_path":file_path}
    
    return dir_data(dir_path,".mp4",lat_func)
    
import re

def get_new_info(line_str):
    # 正则表达式模式
    pattern = r"详情：(\S+):->([^\s]+)-\S{8}\s"
    matches = re.findall(pattern, line_str)
    lst=[]
    for match in matches:
        if not match:
            continue
        url = match[0]
        name = match[1]
        lst.append({"url": url, "name": name}) 
    return lst
def get_old_info(line_str):
    # 正则表达式模式
    pattern = r"【移动文件】-【成功】详情：(\S+) -> ([^-\s]+)"
    matches = re.findall(pattern, line_str)
    lst=[]
    for match in matches:
        if not match:
            continue
        flag = Path(match[0]).parent.name
        name = Path(match[1]).stem
        
        
        
        lst.append({"flag": flag, "name": name}) 
    return lst 
from pathlib import Path
def dir_log_data(dir_path:str)->pd.DataFrame:

    # 定义要搜索的目录
    directory = Path(dir_path)
    lst=[]
    # 遍历目录中的所有文件
    for file_path in directory.glob('**/*trace*.log'):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = file.read()
            infos=get_new_info(data)
            if not infos:
                infos=get_old_info(data)
            if not infos:
                print(f"{file_path} no match")
            else:
                for item in infos:
                    item["log_path"]=file_path 
                lst.extend(infos)
    log_df=pd.json_normalize(lst) 
    log_df.drop_duplicates(subset=["name","url"], keep="first",inplace=True)      
    return log_df
    
    
def analyse_log(log_path:str):
    lst=[]
    with open(log_path, 'r', encoding='utf-8') as file:
        data = file.read()
            # 正则表达式模式

        pattern = r"2025-01-17 (.{8}).*?【下载(\S+)】-【统计】详情：第(\d+)次,已下载(\d+)个,缺失(\d+)个"
        matches = re.findall(pattern, data)
        
        for match in matches:
            if not match:
                continue
            time=match[0]
            name = match[1]
            times=match[2]
            loaded=match[3]
            lost = match[4]
            lst.append({"time": time, "name": name, "times": times, "loaded": loaded, "lost": lost})
    log_df=pd.json_normalize(lst) 
    log_df.sort_values(by=["name","times"],ascending=[True,False],inplace=True)
    log_df.drop_duplicates(subset=["name"], keep="first",inplace=True)  
    
    
        
    return log_df
    
    
if __name__ == "__main__":
    

    # log_df=dir_log_data(r"F:\worm_practice\logs\playlist")
    
    url_path = r"F:\worm_practice\player\urls"
    # log_df.to_excel(os.path.join(url_path,"log_urls.xlsx"))
    # exit(0)
    
    # analyse_df=analyse_log(r"F:\worm_practice\logs\playlist\playlist-trace.log")
    # analyse_df.to_excel(os.path.join(url_path,"analyse_log.xlsx"))
    
    # exit(0)
    
    url_df=dir_url_datas(url_path)
    url_df["len"]=url_df["url"].apply(lambda x:len(x))
    url_df.sort_values(by="len",ascending=True,inplace=True)
    url_df.to_excel(os.path.join(url_path,"log_urls.xlsx"))
    exit(0)
    
    player_df=dir_video_datas(r"F:\worm_practice\player\video")
    db_df=dir_video_datas(r"F:\数据库")
    mp4_df=pd.concat([player_df,db_df],axis=0)
    # print(mp4_df)
    
    temp_df=pd.merge(url_df,mp4_df,on="name",how="outer")
    merge_df=pd.merge(temp_df,log_df,on="name",how="outer")
    
    # 如果 url_y 列有值，则将 url_x 列对应行的值设置为 url_y 列对应行的值
    merge_df.loc[merge_df['url_y'].isna(),"A"]=merge_df['url_y']
    merge_df.drop(columns=['url_y'], inplace=True)
    merge_df.rename(columns={'url_x': 'url'}, inplace=True)
    
    # 将 A 列为空时指定为空字符串，并将 A 列的类型转换为字符串
    merge_df['url'] = merge_df['url'].fillna('').astype(str)
    merge_df["len"]=merge_df["url"].apply(lambda x:len(x))
    merge_df.drop_duplicates(subset=["name","url"], keep="first",inplace=True)
    merge_df.sort_values(by="len",ascending=True,inplace=True)
    merge_df.to_excel(os.path.join(url_path,"merge_urls.xlsx"))
    
    
    
    
    