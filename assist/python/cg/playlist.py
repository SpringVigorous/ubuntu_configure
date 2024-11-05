﻿import requests

import os
import concurrent.futures


from pathlib import Path



import re
import json
import sys

root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )

from base import exception_decorator,logger_helper,except_stack,normal_path,fetch_sync,decrypt_aes_128,get_folder_path
from base import download_sync,move_file,get_homepage_url,is_http_or_https,hash_text,delete_directory,merge_video




class video_info:
    def __init__(self,url) -> None:
        self.method=None
        self.uri=None
        self.iv=None
        
        self.root_url=get_homepage_url(url)
        
        content=requests.get(url).text
        # 正则表达式模式
        self._init_urls(content)
        self._init_keys(content)

    def _init_urls(self,content):
        pattern = re.compile(r'#EXTINF:(.*?),\s*(\S+)\s')


        matches = pattern.findall(content)
        playlist=[]
        for index,val in enumerate(matches) :
            duration, ts_file =val
            playlist.append((index+1,duration,ts_file))
        
        self.playlist=playlist
        
    def _init_keys(self,content):
               
        """
        从给定的字符串中提取 METHOD、URI 和 IV 的值。
    
        :param line: 要处理的字符串
        :return: 包含 METHOD、URI 和 IV 的字典
        """
        # 定义正则表达式模式
        pattern = r'#EXT-X-KEY:METHOD=(?P<method>[^,]+),URI="(?P<uri>[^"]+)",IV=(?P<iv>0x[0-9a-fA-F]+)'
        
        # 使用 re.search 检查字符串是否匹配模式
        match = re.search(pattern, content)
        

        
        # 返回匹配结果
        if match:
            self.method=match.group('method')
            self.uri=match.group('uri')
            self.iv=match.group('iv')



def get_real_url(url,url_pre):
   return   f"{url_pre}{url}" if not is_http_or_https(url) else url

def get_urls(playlist,url_pre):
    url_list=[ get_real_url(url_lat,url_pre)  for url_lat in playlist]
    return url_list



@exception_decorator()
def get_playlist(url):

    responds=requests.get(url)
    # 正则表达式模式
    pattern = re.compile(r'#EXTINF:(.*?),\s*(\S+)\s')


    matches = pattern.findall(responds.text)
    playlist=[]
    for index,val in enumerate(matches) :
        duration, ts_file =val
        playlist.append((index+1,duration,ts_file))
        
        
        
        
    return playlist
    
@exception_decorator()
def handle_playlist(url_list,temp_paths):
    if not url_list or not temp_paths:
        return False
    

    logger= logger_helper("下载文件",Path(temp_paths[0]).parent)
    success=True
    
    # 使用线程池并行下载
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(download_sync, url, temp_path)   for  url,temp_path in zip(url_list,temp_paths)]
        
        # 等待所有任务完成
        for future in concurrent.futures.as_completed(futures):
            try:
                if not future.result():
                    success=False
            except Exception as e:
                logger.error("下载异常",except_stack())
                success=False

    
    return success
            
def temp_paths(count,temp_dir):
    return [normal_path(os.path.join(temp_dir, f"{index+1}.mp4"))    for index in range(count)]


def decryp_video(org_path,dest_path,key,iv):
    data=None
    with open(org_path,"rb") as f:
        encrypted_data=f.read()
        data=decrypt_aes_128(key,iv,encrypted_data)
    if data:
        with open(dest_path,"wb") as f:
            f.write(data)
        
        

def decryp_videos(org_paths,dest_dir,key,iv):
        # 使用线程池并行下载
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        
        futures =[]
        for org_path in zip(org_paths):
            org=Path(org_path)
            dest_path=os.path.join(dest_dir,org.name)
            futures.append(executor.submit(decryp_video, org_path,dest_path, key,ivorg_path,key,iv) )  
        
        # 等待所有任务完成
        for future in concurrent.futures.as_completed(futures):
            try:
                if not future.result():
                    success=False
            except Exception as e:
                logger.error("下载异常",except_stack())
                success=False

    
    return success
    
    
    
    

@exception_decorator()
def main(url,url_pre,dest_name):
    root_path="F:/worm_practice/player/"
    dest_hash=hash_text(dest_name)
    temp_decode_dir= os.path.join(root_path,"temp",dest_hash) 
    temp_path=normal_path(os.path.join(temp_decode_dir,f"{dest_hash}.mp4")) 
    dest_path=normal_path(os.path.join(root_path,f"{dest_hash}.mp4"))
    
    

        
    os.makedirs(temp_decode_dir, exist_ok=True)
    
    info_list=get_playlist(url)
    if not info_list:
        return
    with open(os.path.join(temp_decode_dir,"url.txt"),"w",encoding="utf-8-sig") as f:
        json.dump(info_list,f,ensure_ascii=False,indent=4)
    

    if not url_pre:
        url_pre=get_homepage_url(url)
        
    url_list=[get_real_url(urls[2],url_pre)  for urls in info_list]
    temp_path_list=temp_paths(len(url_list),temp_decode_dir)
    
    
    success=handle_playlist(url_list,temp_path_list)
    if not success:
        return
    
    decryp_videos(url_list,temp_decode_dir,key,iv)
    
    merge_video(temp_path_list,temp_path)
    move_file(temp_path,dest_path)
    
    # delete_directory(temp_dir)
    
    
    
def get_key(url):

    key=fetch_sync(url)
    return key
    
if __name__=="__main__":
    
    
    lst=[
        # ("https://vip.lz-cdn.com/20220917/33091_abc5295d/1200k/hls/mixed.m3u8","https://vip.lz-cdn.com/20220917/33091_abc5295d/1200k/hls/","3D肉蒲团1"),
        # ("https://ikcdn01.ikzybf.com/20240422/zaL0A0dC/2000kb/hls/index.m3u8","https://kkzycdn.com:65/20240422/zaL0A0dC/2000kb/hls/","3D肉蒲团"),
        # ("https://v8.tlkqc.com/wjv8/202310/09/6FnT1gEfrp1/video/1000k_720/hls/index.m3u8","","金瓶梅2008"),
        # ("https://ukzyll.ukubf6.com/20220526/9ROENkuT/2000kb/hls/index.m3u8","https://ukzyll.ukubf6.com","金瓶梅2"),
        # ("https://ukzy.ukubf4.com/20220403/Gf23AIB0/2000kb/hls/index.m3u8","https://ukzy.ukubf4.com","四大名捕之入梦妖灵"),
        # ("https://hd.ijycnd.com/play/negMER9b/index.m3u8","","金瓶梅II爱的奴隶"),
        ("https://hd.ijycnd.com/play/Le32QD9d/index.m3u8","","隔壁的呻吟声"),
        # ("https://ikcdn01.ikzybf.com/20221201/6iQAY1nx/2000kb/hls/index.m3u8","","波多野结衣之双飞调教"),
        
    ]
    # for url,url_pre,dest_name in lst:
    #     main(url,url_pre,dest_name)

    key=get_key("https://hd.ijycnd.com/play/Le32QD9d/enc.key")
    
    IV=0x00000000000000000000000000000000

    val=video_info("https://hd.ijycnd.com/play/Le32QD9d/index.m3u8")

    decryp_video(r"F:\worm_practice\player\temp\feb6b940-1\1.mp4",r"F:\worm_practice\player\temp\feb6b940\1.mp4",key,IV)