import requests

import os
import concurrent.futures


from pathlib import Path

import operator

import re
import json
import sys
import asyncio

root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )

from base import exception_decorator,logger_helper,except_stack,normal_path,fetch_sync,decrypt_aes_128,get_folder_path,UpdateTimeType
from base import download_async,download_sync,move_file,get_homepage_url,is_http_or_https,hash_text,delete_directory,merge_video,convert_video_to_mp4_from_src_dir,convert_video_to_mp4,get_all_files_pathlib,move_file
from base import as_normal,MultiThreadCoroutine





class video_info:
    def __init__(self,url) -> None:
        self.url=url
        self.method=None
        self.uri=None
        self.iv=None
        response=requests.get(url)
        content=response.text
        # print(content)
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
            self.iv=bytes.fromhex(match.group('iv').replace('0x',''))
            
    @property
    def key(self):
        if not self.uri:
            return None
        
        org_path=Path(self.url)
        name=org_path.name
        url=self.url.replace(name,self.uri)
        return fetch_sync(url)

    @property
    def domain(self):
        return get_homepage_url(self.url)


def get_real_url(url:str,url_page):
    if is_http_or_https(url) :
        return url
    if url[:1]==r'/':
        return   f"{get_homepage_url(url_page) }{url}"
    else:
        org_path=Path(url_page)
        name=org_path.name
        return url_page.replace(name,url)
    




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
def handle_playlist(url_list,temp_paths,key,iv):
    if not url_list or not temp_paths:
        return False
    

    playlist_logger= logger_helper("下载文件",Path(temp_paths[0]).parent)

    playlist_logger.trace("开始")
    def decode():
        if not key or not iv:
            return None 
        def _decode(encrypted_data):
            return decrypt_aes_128(key,iv,encrypted_data)
        return _decode
    
    async def download(semaphore,args:list|tuple):
        async with semaphore:
            url, temp_path=args
            result=  await download_async(url, temp_path,decode()) 
            
            #转换为标准的mp4,看需求 转换
            # is_convert=True
            # if result and is_convert:
            #     org_path=Path(temp_path)
            #     output_path = os.path.join(f"{org_path.parent}_output",org_path.stem + '.mp4')
            #     os.makedirs(os.path.dirname(output_path), exist_ok=True)
            #     convert_video_to_mp4(temp_path,output_path)
            #     move_file(output_path,temp_path)

            
            return result
    lst=[(url,path) for url,path in zip(url_list,temp_paths) if not os.path.exists(path) ]
    if not lst:
        return True
    multi_thread_coroutine = MultiThreadCoroutine(download,lst)
    try:
        asyncio.run(multi_thread_coroutine.run_tasks()) 
        success=multi_thread_coroutine.success
        if not success:
            info=[multi_thread_coroutine.fail_infos,except_stack()]
            info_str="\n".join(info)
            playlist_logger.error("异常",f"\n{info_str}\n",update_time_type=UpdateTimeType.ALL)
        print(multi_thread_coroutine.result)
        
        return multi_thread_coroutine.success
    except Exception as e:
        playlist_logger.error("下载异常",except_stack(),update_time_type=UpdateTimeType.ALL)
        return False
    
def process_playlist(url_list, temp_path_list, key, iv, root_path, dest_name, dest_hash):
    play_logger=logger_helper(f"下载{dest_name}")
    
    download_time=1
    lost_count = 0
    success =False
    already_path_list = []
    while True:
        play_logger.update_target(detail=f"第{download_time}次")
        play_logger.info("开始", update_time_type=UpdateTimeType.ALL)
        success = handle_playlist(url_list, temp_path_list, key, iv)
        play_logger.info("完成", update_time_type=UpdateTimeType.ALL)
        download_time+=1
        if success:
            return True,0,temp_path_list
        else:
            losts = []
            already_path_list = []
            for item in temp_path_list:
                if os.path.exists(item):
                    already_path_list.append(item)
                else:
                    losts.append(item)
            lost_count = len(losts)
            with open(os.path.join(root_path, "urls", f"{dest_name}-{dest_hash}-lost.json"), "w", encoding="utf-8-sig") as f:
                lost_data = {"count": len(losts), "data": losts}
                json.dump(lost_data, f, ensure_ascii=False, indent=4)
                
            play_logger.info("统计",f"已下载{len(already_path_list)}个,缺失{lost_count}个",update_time_type=UpdateTimeType.ALL)
                
        if download_time>10 or lost_count<1:
            break
    
    return success,lost_count,already_path_list
            
def temp_paths(count,temp_dir):
    return [normal_path(os.path.join(temp_dir, f"{index:04}.mp4"))    for index in range(count)]


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
            futures.append(executor.submit(decryp_video, org_path,dest_path, key,iv) )  
        
        # 等待所有任务完成
        for future in concurrent.futures.as_completed(futures):
            try:
                if not future.result():
                    success=False
            except Exception as e:

                success=False

    
    return success
    
    
def load_url_data(url_json_path):
    if  not os.path.exists(url_json_path):
        return
    with open(url_json_path,"r",encoding="utf-8-sig") as f:
        data=json.load(f)
        return data
    return None
    
def save_url_data(url_json_path,data):
    with open(url_json_path,"w",encoding="utf-8-sig") as f:
        json.dump(data,f,ensure_ascii=False,indent=4)


def get_url_data(url,url_json_path):
    info=load_url_data(url_json_path)
    if not info:
        video=video_info(url)
        key= video.key
        iv=video.iv
        info_list=video.playlist
        if not info_list:
            return
        total_len= [float(item[1])   for item in info_list]
        temp=os.path.basename(url_json_path)
        
        dest_name,dest_hash=os.path.basename(url_json_path).split(".")[0].split("-")
        info={"url":url,"name":dest_name,"hash":dest_hash,"total_len":sum(total_len),"key":key,"iv":iv ,"playlist":info_list}
        #保存
        save_url_data(url_json_path,info)
        
    return info.get("key",""),info.get("iv",""),info.get("playlist",[]),info.get("total_len",0)
        
    
@exception_decorator()
def main(url,dest_name,dest_dir:str=None,force_merge=False):
    root_path="F:/worm_practice/player/"
    dest_hash=hash_text(dest_name)
    temp_dir= os.path.join(root_path,"temp",dest_hash) 
    temp_path=normal_path(os.path.join(temp_dir,f"{dest_hash}.mp4")) 
    dest_path=normal_path(os.path.join(root_path,"video",f"{dest_name}.mp4")) if not dest_dir else normal_path(os.path.join(dest_dir,f"{dest_name}.mp4"))
    
    play_logger= logger_helper("下载",f"{url}->{dest_name}-{dest_hash}")
    play_logger.info("开始")
        
    os.makedirs(temp_dir, exist_ok=True)
    
    #加载已有数据
    url_json_path=os.path.join(root_path,"urls",f"{dest_name}-{dest_hash}.json")
    key,iv,info_list,total_len=get_url_data(url,url_json_path)
    play_logger.info(f"总时长:{total_len}s",update_time_type=UpdateTimeType.ALL)
        
    url_list=[get_real_url(urls[2],url)  for urls in info_list]
    temp_path_list=temp_paths(len(url_list),temp_dir)
    
    play_logger.info("开始","下载",update_time_type=UpdateTimeType.ALL)




    success,lost_count,temp_path_list=process_playlist(url_list, temp_path_list, key, iv, root_path, dest_name, dest_hash)

    # decryp_video(org_path,dest_path,key,iv)
    
    # decryp_videos(url_list,temp_decode_dir,key,iv)
    
    #提前退出,避免合并
    # if lost_count>0 and not force_merge:
    #     return True
    
    
    play_logger.info("开始","合并",update_time_type=UpdateTimeType.ALL)
    merge_video(temp_path_list,temp_path)
    play_logger.info("完成","合并",update_time_type=UpdateTimeType.ALL)
    
    move_file(temp_path,dest_path)
    
    if success:
        delete_directory(temp_dir)
        play_logger.info("完成" ,update_time_type=UpdateTimeType.ALL)
    else:
        play_logger.error("部分缺失",f"缺失{lost_count}个文件",update_time_type=UpdateTimeType.ALL)
        
    return True
    
def get_key(url):

    key=fetch_sync(url)
    return key
    
    
    
    

if __name__=="__main__":
    
    
    # temp_dir=r"E:\FFOutput"
    # suffix=[".mp4"]
    # # convert_video_to_mp4_from_src_dir(temp_dir,suffix)

    # temp_path_list=get_all_files_pathlib(temp_dir,suffix)
    # dest_dir=r"F:\worm_practice\player"
    # temp_name="1111.mp4"
    # dest_name="13.mp4"
    # temp_path=f"{dest_dir}\\{temp_name}"
    # merge_video(temp_path_list,temp_path)
    # move_file(temp_path,f"{dest_dir}\\{dest_name}")
    # exit(0)
    
    lst=[
        ("https://live80976.vod.bjmantis.net/cb9fc2e3vodsh1500015158/b78d41a31397757896585883263/playlist_eof.m3u8?t=67882F57&us=6658sy3vu3&sign=86f52ae9c6bd64c87db0ac9937096df9","ai好课_第三课",r"F:\教程\短视频教程\ai好课",False),
    ]
    
    # names=[print(name[2],hash_text(name[2]))  for name in lst]
    
    
    
    result=[main(url,url_pre,dest_name,*args) for url,url_pre,dest_name,*args in lst]
    
    exit(0)
    # if all(result):    
    if True:    
        import os
        os.system("shutdown /s /t 60")
    else:
        print("有失败")
    # key=get_key("https://hd.ijycnd.com/play/Le32QD9d/enc.key")

    # iv=bytes.fromhex("00000000000000000000000000000000")

    # # val=video_info("https://hd.ijycnd.com/play/Le32QD9d/index.m3u8")
    
    # org_path=r"F:\worm_practice\player\temp\feb6b940-1\1.mp4"
    # dest_path=r"F:\worm_practice\player\temp\feb6b940\1.mp4"
    
    # decryp_video(org_path,dest_path,key,iv)
