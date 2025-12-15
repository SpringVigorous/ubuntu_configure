import json
import re
import pandas as pd
import sys
import os
from pathlib import Path
import ast




from base.path_tools import get_all_files_pathlib
from base import logger_root,player_root,df_empty,exception_decorator,concat_dfs,find_rows_by_col_val,downloads_async,log_files,find_last_value_by_col_val,logger_helper,UpdateTimeType,global_logger,read_from_txt,read_from_txt_utf8_sig
import asyncio

from audio_manager import *

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
    
def handle_urls():
    # log_df=dir_log_data(worm_root/r"logs\playlist")
    from base import worm_root
    
    url_path =worm_root/r"player\urls"
    # log_df.to_excel(os.path.join(url_path,"log_urls.xlsx"))
    # exit(0)
    
    # analyse_df=analyse_log(worm_root/r"logs\playlist\playlist-trace.log")
    # analyse_df.to_excel(os.path.join(url_path,"analyse_log.xlsx"))
    
    # exit(0)
    
    url_df=dir_url_datas(url_path)
    url_df["len"]=url_df["url"].apply(lambda x:len(x))
    url_df.sort_values(by="len",ascending=True,inplace=True)
    url_df.to_excel(os.path.join(url_path,"log_urls.xlsx"))
    exit(0)
    
    player_df=dir_video_datas(worm_root/r"player\video")
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
    
def video_info_from_log(log_path:str):
    lst=[]
    data=read_from_txt_utf8_sig(log_path)
    if not data:
        return
        
    # 正则表达式模式
    #【更新xlsx】-【成功】详情：收到第24个消息:title:HD中字完整在线观看 url:https://yenchuang.com/d/103546/6847620974287.html m3u8_url:https://s1.bfllvip.com/video/pengyoumamawufarenshouderizi/HD%E4%B8%AD%E5%AD%97/index.m3u8 download:-1 m3u8_hash:33c490e5fdd468d60e36fa75387a3f166c755f6961f957953d42bb86caedd375,key:None,
    pattern=r"【更新xlsx】-【成功】详情：收到第\d+个消息:title:(.*?) url:(.*?) m3u8_url:(.*?) download:(.*?) m3u8_hash:(.*?),key:(.*?)(?:,|\n)"
    matches = re.findall(pattern, data)
    
    for match in matches:
        if not match:
            continue
        title, url, m3u8_url, download, m3u8_hash, key = [item.strip() if item != 'None' else None for item in match]
        lst.append({"title": title, "url": url, "m3u8_url": m3u8_url, "m3u8_hash": m3u8_hash, 'download':download})
    log_df=pd.json_normalize(lst) 
    pattern=r"【更新下载状态】-【已下载】详情：(.*?),耗时"
    matches = re.findall(pattern, data)
    
    result_lst=[]
    for match in matches:
        if not match:
            continue
        title=match
        result_lst.append(title)

        
    pattern=r"【下载视频...】-【完成】详情：(.*?),耗时"
    already_download_lst=[]
    matches = re.findall(pattern, data)
    for match in matches:
        if not match:
            continue
        title=match
        already_download_lst.append(title)
        
    patial_download_lst=[]
    pattern=r"【下载视频...】-【开始】详情：(.*?)"
    matches = re.findall(pattern, data)
    for match in matches:
        if not match:
            continue
        title=match
        if title in already_download_lst:
            continue
        patial_download_lst.append(title)
        
        
    log_df["download"]=log_df["title"].apply(lambda x:1 if x in result_lst else -1)
    log_df.drop_duplicates(subset=["title"], keep="last",inplace=True)
    
    org_path=Path(log_path)
    log_df.to_excel(org_path.parent.joinpath(org_path.stem+"_info.xlsx"))
    return log_df

@exception_decorator(error_state=False)
def str_to_dict(cleaned_str:str):
    try:
        # 使用 ast.literal_eval 安全转换
        return ast.literal_eval(cleaned_str)
    except (ValueError, SyntaxError) as e:
        # 如果转换失败，尝试修复常见问题
        try:
            # 尝试将单引号转换为双引号（JSON格式）
            json_str = cleaned_str.replace("'", "\"")
            import json
            return json.loads(json_str)
        except:
            pass
        
        
@exception_decorator(error_state=False)
def handle_audio_from_log(log_path:str)->list[dict]:
    if not log_path or not os.path.exists(log_path):
        return

    lst=[]
    data=None
    with open(log_path, 'r', encoding='utf-8-sig') as file:
        data = file.read()
        
    # 正则表达式模式
    msg_pattern=r"(.*?)-TRACE-.*?更新下载状态及文件后缀】-【成功】详情：(.*?),耗时："
    matches = re.findall(msg_pattern, data)
    
    path_reg=re.compile( r"WindowsPath\(('[^']*'|\"[^\"]*\")\)")
    # 1. 修复未加引号的字符串值
    
    status_reg=re.compile( r"('status':\s*)([^,]*)" )
    for match in matches:
        if not match:
            continue
        msg_time=match[0]
        msg=path_reg.sub(r"\1", match[1])
        msg=status_reg.sub( r'\1"\2"', msg)
        
        if result:=str_to_dict(msg):
            result["msg_time"]=msg_time
            lst.append(result)
    return lst

@exception_decorator(error_state=False)
def fetch_author_url_from_log(log_path:str)->list[str]:
    data=read_from_txt(log_path)
    if not data:
        return    
        
    # 正则表达式模式
    msg_pattern=r"(https://www.ximalaya.com/zhubo/[a-zA-Z0-9]+)"
    matches = re.findall(msg_pattern, data)

    return matches

@exception_decorator(error_state=False)
def fetch_author_url_from_logs(log_paths:list[str])->list[str]:
    results=[]
    for log_path in log_paths:
        if result:=fetch_author_url_from_log(log_path):
            results.extend(result)
    return unique(results)


def handle_audio_from_logs(log_paths:list[str])->pd.DataFrame:
    results=[]
    for log_path in log_paths:
        if result:=handle_audio_from_log(log_path):
            results.extend(result)
        # break
    
    df=pd.DataFrame(results)
    if df_empty(df):
        return
    # df.dropna(subset=[])
    df.drop_duplicates(subset=["sound_url"],inplace=True,keep="last")
    mask=(df["status"]!="下载成功") & df["media_url"].notna()
    df=df[mask].copy()
    manager=  AudioManager()
    
    dfs=[]
    for xlsx_path,group in df.groupby("xlsx_path", group_keys=False):
        row=group.iloc[0]
        sheet_name=row["sheet_name"]
        album_df=manager.get_df(xlsx_path,sheet_name)
        if df_empty(album_df):
            continue
        
        def find_local_path(sound_url:str):
            
            dest_path=find_last_value_by_col_val(album_df,href_id,sound_url,local_path_id)
            #有效，但未下载
            return dest_path if dest_path and  not os.path.exists(dest_path) else None

        
        group[local_path_id]=group["sound_url"].apply(find_local_path)
        group[name_id]=group[local_path_id].apply(lambda x: Path(x).stem if x else None)
        dfs.append(group)
        
    df=concat_dfs(dfs)
    df.dropna(subset=[name_id],inplace=True)
    try:
        df.to_excel(Path(log_paths[0]).with_suffix(".xlsx"),index=False)
    except:
        pass
    return df



    

async def download_task():
    
    df=pd.read_excel(logger_root/r"audio_app\audio_app-trace.xlsx")
    manager=  AudioManager()
    lst=[]
    for index,row in df.iterrows():
        xlsx_path,sheet_name,media_url,sound_url=row["xlsx_path"],row["sheet_name"],row["media_url"],row["sound_url"]
        album_df=manager.get_df(xlsx_path,sheet_name)
        if df_empty(album_df):
            continue
        for index,dest_row in find_rows_by_col_val(album_df,href_id,sound_url).iterrows():
            dest_path=dest_row[local_path_id]
            if os.path.exists(dest_path):
                continue
            lst.append((media_url,dest_path))
            
    if not lst:
        return 
    url_lst,dest_lst=zip(*lst)
    headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Range': 'bytes=0-',
            'Referer': 'https://www.ximalaya.com/',
            'Sec-Fetch-Dest': 'audio',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.97 Safari/537.36 SE 2.X MetaSr 1.0',
            'sec-ch-ua': '"Not)A;Brand";v="24", "Chromium";v="116"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
    return await downloads_async(url_lst,dest_lst,headers=headers)
    

@exception_decorator(error_state=False)
def download_audio_by_log():
    # log_lst=[file_path for file_path in log_files(logger_root/r"audio_app") if  "trace" in Path(file_path).stem]
    log_lst=[file_path for file_path in log_files(logger_root/r"audio_app") if  "audio_app-trace"== Path(file_path).stem]
    
    logger=logger_helper("通过日志信息下载音频",f'日志路径为：\n{"\n".join(log_lst)}\n')
    
    # results=fetch_author_url_from_logs(log_lst)
    # logger.info("完成",f"\n{'\n'.join(results)}\n",update_time_type=UpdateTimeType.ALL)
    # return
    
    df=handle_audio_from_logs(log_lst)
    if df_empty(df) :
        return
    result=asyncio.run(download_task())
    
    logger.info("完成",f"共{len(df)}个,成功{result.count(True)}个",update_time_type=UpdateTimeType.ALL)

if __name__ == "__main__":
    
    # download_audio_by_log()
        

        
    # exit()
    # df=handle_info_from_log(logger_root/r"playlist_app\playlist_app-info.log.2025-12-14.log")
    df=video_info_from_log(logger_root/r"playlist_app\playlist_app-info.log")
    
    xlsx_path=player_root/r"video.xlsx"
    org_df=pd.read_excel(xlsx_path,sheet_name="video")
    from base import concat_dfs
    dest_df=concat_dfs([org_df,df])
    dest_df.drop_duplicates(subset=["title"], keep="last",inplace=True)
    
    dest_df.to_excel(xlsx_path,sheet_name="video")
    pass

    
    
    
    