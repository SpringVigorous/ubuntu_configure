import requests

import os
import concurrent.futures


from pathlib import Path



import re
import json
import sys
import asyncio

root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )


from base import exception_decorator,logger_helper,except_stack,normal_path,fetch_sync,decrypt_aes_128_from_key,get_folder_path,UpdateTimeType
from base import download_async,download_sync,move_file,get_homepage_url,is_http_or_https,hash_text,delete_directory,merge_video,convert_video_to_mp4_from_src_dir,convert_video_to_mp4,get_all_files_pathlib,move_file
from base import as_normal,MultiThreadCoroutine
from urls_tools import arrange_urls,postfix
import pandas as pd


from base import exception_decorator,base64_utf8_to_bytes,bytes_to_base64_utf8
def get_real_url(url:str,url_page):
    if is_http_or_https(url) :
        return url
    if url[:1]==r'/':
        return   f"{get_homepage_url(url_page) }{url}"
    else:
        org_path=Path(url_page)
        name=org_path.name
        return url_page.replace(name,url)




class video_info:
    def __init__(self,url) -> None:
        self.url=url
        self.method=None
        self.uri=None
        self.iv=None
        # https://live80976.vod.bjmantis.net/cb9fc2e3vodsh1500015158/b78d41a31397757896585883263/playlist_eof.m3u8?t=67882F57&us=6658sy3vu3&sign=86f52ae9c6bd64c87db0ac9937096df9
        headers = {
            'Connection': 'keep-alive',
            'sec-ch-ua': '";Not A Brand";v="99", "Chromium";v="94"',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 SE 2.X MetaSr 1.0',
            'sec-ch-ua-platform': '"Windows"',
            'Accept': '*/*',
            'Origin': 'https://haokeyouxuanedu.edu.gzfeice.com',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://haokeyouxuanedu.edu.gzfeice.com/',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }


        
        
        response=requests.get(url, headers=headers)
        self.logger=logger_helper("解析m3u8",f"{self.url}")

        content=response.text
        try:
            header=content.split('#EXTINF:')[0].replace(",","\n")

            self.logger.info("内容头",f"\n{header}\n")
        except:
            pass
        # print(content)
        # 正则表达式模式
        self._init_urls(content)
        self._init_keys(content)

    def _init_urls(self,content):
        pattern = re.compile(r'#EXTINF:(.*?),\s*(\S+)\s')

        matches = pattern.findall(content)
        playlist=[]
        for val in matches :
            duration, ts_file =val
            playlist.append([float(duration),get_real_url(ts_file,self.url)])
        
        arrage_lst= arrange_urls(playlist)   
            
        dest_list=[[index,seg["duration"],seg["url"]]    for index,seg in enumerate(arrage_lst)]
        
        self.playlist=dest_list
        self.org_playlist=[[index,*seg]   for index,seg in enumerate(playlist)  ]
        
    @property
    def has_raw_list(self):
        return len(self.org_playlist)>len(self.playlist)
        
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
            iv=match.group('iv')
            self.iv=bytes.fromhex(iv.replace('0x',''))


            
    @property
    def key(self):
        if not self.uri:
            return None
        url=self.uri
        if not is_http_or_https(url):

            org_path=Path(self.url)
            name=org_path.name
            url=self.url.replace(name,self.uri)
        key=fetch_sync(url)


        self.logger.info("加密信息",f"\nmethod:{self.method},\nuri:{self.uri},\niv:{self.iv},\nkey:{key}")
        # print(len(self.iv))
        # print(len(key))
        return key

    @property
    def domain(self):
        return get_homepage_url(self.url)



    

    

        


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
            return decrypt_aes_128_from_key(key,iv,encrypted_data)
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
    
def process_playlist(url_list, all_path_list, key, iv, root_path, dest_name, dest_hash):
    play_logger=logger_helper(f"{dest_name}")
    
    download_time=1
    all_count=len(url_list)
    lost_count = 0
    success =False

    
    urls=url_list.copy()
    temp_paths=all_path_list.copy()
    success_paths=[]
    last_lost_count=0
    
    while True:
        play_logger.update_target(detail=f"第{download_time}次")
        play_logger.info("开始", update_time_type=UpdateTimeType.ALL)
        success = handle_playlist(urls, temp_paths, key, iv)
        play_logger.info("完成", update_time_type=UpdateTimeType.ALL)
        download_time+=1
        
        #检查下载情况
        if success:
            return 0,all_path_list
        else:
            losts = []

            for url,temp_path in  zip(urls,temp_paths):
                if not os.path.exists(temp_path):
                    losts.append({"url":url,"path":temp_path})
                else:
                    success_paths.append(temp_path)
            lost_count = len(losts)
            play_logger.info("统计",f"已下载{all_count-lost_count}个,缺失{lost_count}个",update_time_type=UpdateTimeType.ALL)
                
        if download_time>10 or lost_count<1 or (last_lost_count==lost_count):
            break
        last_lost_count=lost_count
        
    #输出未成功下载的文件信息
    if lost_count>0:    
        with open(os.path.join(root_path, "urls", f"{dest_name}-{dest_hash}-lost.json"), "w", encoding="utf-8-sig") as f:
            lost_data = {"count": len(losts),"time":download_time, "data": losts}
            json.dump(lost_data, f, ensure_ascii=False, indent=4)
            
            
    lost_path=[temp_path   for item in losts for _,temp_path in item.items()]  
    success_paths=[item for item in all_path_list if item not in lost_path]
    return lost_count,success_paths
            
def temp_video_paths(count,temp_dir,postfix=".mp4"):
    return [normal_path(os.path.join(temp_dir, f"{index:04}{postfix}"))    for index in range(count)]


def decryp_video(org_path,dest_path,key,iv):
    data=None
    with open(org_path,"rb") as f:
        encrypted_data=f.read()
        data=decrypt_aes_128_from_key(key,iv,encrypted_data)
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
    
    
@exception_decorator()
def load_url_data(url_json_path):
    if  not os.path.exists(url_json_path):
        return
    with open(url_json_path,"r",encoding="utf-8-sig") as f:
        data=json.load(f)
        return data
    return None
    
@exception_decorator()
def save_url_data(url_json_path,data):
    with open(url_json_path,"w",encoding="utf-8-sig") as f:
        json.dump(data,f,ensure_ascii=False,indent=4)


@exception_decorator()
def get_url_data(url,url_json_path):
    info=load_url_data(url_json_path)
    if not info:
        video=video_info(url)
        key= video.key
        iv=video.iv

        if key :
            key= bytes_to_base64_utf8(key)
        if iv :
            iv= bytes_to_base64_utf8(iv)


        info_list=video.playlist
        if not info_list:
            return
        total_len= [float(item[1])   for item in info_list]
        temp=os.path.basename(url_json_path)
        
        dest_name,dest_hash=temp.split(".")[0].split("-")
        info={"url":url,"name":dest_name,"hash":dest_hash,"total_len":sum(total_len),"key":key,"iv":iv ,"playlist":info_list}
        if video.has_raw_list:
            info["org_playlist"]=video.org_playlist
        
        
        #保存
        save_url_data(url_json_path,info)

    try:    
        key=info.get("key","")
        iv=info.get("iv","")
        if key:
            key=base64_utf8_to_bytes(key)
        if iv:
            iv=base64_utf8_to_bytes(iv)
        # return None,None,info.get("playlist",[]),info.get("total_len",0)
        return key,iv,info.get("playlist",[]),info.get("total_len",0)
    except:
        return None,None,info.get("playlist",[]),info.get("total_len",0)
        
    
@exception_decorator()
def main(url,dest_name,dest_dir:str=None,force_merge=False):
    root_path="D:/Project/worm_practice/player/"
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
    # url_list=[get_real_url(urls[2],url)  for urls in info_list]
    url_list=[get_real_url(urls[2],url)  for urls in info_list]
    play_logger.info(f"总时长:{total_len}s,共{len(url_list)}个",update_time_type=UpdateTimeType.ALL)

    
    temp_path_list=temp_video_paths(len(url_list),temp_dir,postfix(url_list[0]))
    
    play_logger.info("开始","下载",update_time_type=UpdateTimeType.ALL)

    lost_count,success_paths=process_playlist(url_list, temp_path_list, key, iv, root_path, dest_name, dest_hash)

    # decryp_video(org_path,dest_path,key,iv)
    
    # decryp_videos(url_list,temp_decode_dir,key,iv)
    
    #提前退出,避免合并
    # if lost_count>0 and not force_merge:
    #     return True
    
    # return True
    
    play_logger.info("开始","合并",update_time_type=UpdateTimeType.ALL)
    merge_video(success_paths,temp_path)
    play_logger.info("完成","合并",update_time_type=UpdateTimeType.ALL)
    
    move_file(temp_path,dest_path)
    
    if lost_count==0 :
        # delete_directory(temp_dir)
        play_logger.info("完成" ,update_time_type=UpdateTimeType.ALL)
    else:
        play_logger.error("部分缺失",f"缺失{lost_count}个文件",update_time_type=UpdateTimeType.ALL)
        
    return True
    
def get_key(url):

    key=fetch_sync(url)
    return key
from pathlib import Path


def rename_postfix(file_path, postfix):
    cur_path=Path(file_path)
    dest_path=cur_path.with_suffix(postfix)
    return cur_path.rename(dest_path)

def rename_ts(dir_path,postfix=".jpeg"):

       # 遍历目录中的所有文件
    for file in get_all_files_pathlib(dir_path,[postfix]):
        rename_postfix(file,postfix)


     
    
    
def force_merge(dir_path,dest_path):
    temp_path_list=get_all_files_pathlib(dir_path,[".ts"])
    temp_path=f"F:/worm_practice/player/temp/{hash_text(dest_path)}.mp4"
    merge_video(temp_path_list,temp_path)
    move_file(temp_path,dest_path)
    delete_directory(dir_path)
def shut_down(time:10):
    os.system(f"shutdown /s /t {time}")
def force_merges():
    raw_df=pd.read_excel(r"F:\worm_practice\player\urls\log_urls.xlsx",index_col=1)
    already_df=pd.read_excel(r"F:\worm_practice\player\urls\hash_path.xlsx")
    dest_dir=r"F:\worm_practice\player\video"
    
    already_df["hash"]=already_df["hash_path"].apply(lambda x:Path(x).name)
    merge_df=pd.merge(already_df,raw_df,on="hash",how="inner")
    for index,row in merge_df.iterrows():
        force_merge(row["hash_path"],os.path.join(dest_dir,f"{row["name"]}.mp4")) 
    
    shut_down(10)

if __name__=="__main__":
    
    # force_merges()
    # exit(0)
    
    # val=rename_postfix(r"F:\worm_practice\player\temp\46256563\0000.jpeg",".ts")
    # print(val)
    # exit(0)
    # temp_dir=r"F:\worm_practice\player\temp"
    # rename_ts(temp_dir,".jpeg")
    # exit(0)
    # force_merge(temp_dir,r"F:\worm_practice\player\video\1.mp4")
    # exit(0)
    
    
    # temp_dir=r"E:\FFOutput"
    # suffix=[".mp4"]
    # # convert_video_to_mp4_from_src_dir(temp_dir,suffix)

    # temp_path_list=get_all_files_pathlib(temp_dir,suffix)
    # dest_dir=r"F:\worm_practice\player"
    # temp_name="1111.mp4"
    # dest_name="13.mp4"
    # temp_path=f"{dest_dir}/{temp_name}"
    # merge_video(temp_path_list,temp_path)
    # move_file(temp_path,f"{dest_dir}/{dest_name}")
    # exit(0)
    
    lst=[


        ("https://video.gzfeice.cn/b7554d95vodtranscq1254019786/5296e01c1397757903358079695/voddrm.token.eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9~eyJ0eXBlIjoiRHJtVG9rZW4iLCJhcHBJZCI6MTI1NDAxOTc4NiwiZmlsZUlkIjoiMTM5Nzc1NzkwMzM1ODA3OTY5NSIsImN1cnJlbnRUaW1lU3RhbXAiOjAsImV4cGlyZVRpbWVTdGFtcCI6MjE0NzQ4MzY0NywicmFuZG9tIjowLCJvdmVybGF5S2V5IjoiIiwib3ZlcmxheUl2IjoiIiwiY2lwaGVyZWRPdmVybGF5S2V5IjoiNmM1OGI3YThiMWRmODA5NWM2NThmNDUyNDYxMmZkZWEwOWRlMGZmMTVmZDU1MmZlNmJkYWFjYzBjMGE3M2ExNGVlZjk2ZWVjOThiNTNjYTg0Y2U3NmNkYzcyYjQwZWViYmQ5ODM4N2FkMjMxNzE1MjNiMTI4MmYxYThlY2Y3YTU4ZjY3MDJhZmY5YzIzNGE1ZDA4YjJiNGIzYjM2MmNlM2FkZmFkMTAwOWY2NzBkMzNmYWNhOWI3MGUzNzhlY2IxZGM1MDQyMzZmYzFlZjY4ZmU0OTk3ZjdiYzZkMWI0MmMzMjQzOGEyZmNmMzIxZWQzOTY5MGUzNzU1MjM0NGZiMCIsImNpcGhlcmVkT3ZlcmxheUl2IjoiMjZjYzdiZDg4ZmQ2NjRmYjVlNDQyZjIwN2E3YThhMTk2NDRlMmQ5MDVlZmVlNjZhMmZlNTlmNGRjZGQyYjdmYWQxNzI4MjBiZThiODlhOTc0MjU2OTNjZTE1YzA3MDU5NGM2ZWU3M2EzMDI3ODk3Y2RhMjE0YTkzZmQ5OWQ1N2I3NDFmY2VkMDc1MDk2N2JkMDhmMzVlYjBlODFmZjgxNjYwYjg5MmFkZjI4YmQ0ZDQwNjQxZjc1OTg5ZWRlYmNkYjM1NDU3MDA5MGM5NjQzNTcxOGJkZWM2Y2UzZjI4YWVkZGI2ZmM2OWFlMzhhOTVmYzdkMGRiNDA3NDY1MWU4ZiIsImtleUlkIjoxLCJzdHJpY3RNb2RlIjowLCJwZXJzaXN0ZW50IjoiIiwicmVudGFsRHVyYXRpb24iOjAsImZvcmNlTDFUcmFja1R5cGVzIjpudWxsfQ~Evr4YUvlcwsHH_1xkr7WbKdXbVPD-qvelazjBW1R9iM.video_1444917_2.m3u8?encdomain=cmv1","外包项目分享课",r"D:\Project\教程\Python全栈0基础入门",False),
        ("https://video.gzfeice.cn/b7554d95vodtranscq1254019786/195f12ff1397757889910859613/voddrm.token.eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9~eyJ0eXBlIjoiRHJtVG9rZW4iLCJhcHBJZCI6MTI1NDAxOTc4NiwiZmlsZUlkIjoiMTM5Nzc1Nzg4OTkxMDg1OTYxMyIsImN1cnJlbnRUaW1lU3RhbXAiOjAsImV4cGlyZVRpbWVTdGFtcCI6MjE0NzQ4MzY0NywicmFuZG9tIjowLCJvdmVybGF5S2V5IjoiIiwib3ZlcmxheUl2IjoiIiwiY2lwaGVyZWRPdmVybGF5S2V5IjoiMWQxYWY0ZGY5NjI1MDI0NDg4OGE4MmE1Mzc2Y2RkODY1Y2QxNDNhMTBiNGM2MDIxOGMxNmFlMzZjNDc5YWFiZmE4MzA4Y2ZlM2YyNmNmMDg2Y2U5ZTMyMjYxZTBhZGM2Yjc3OWZiMWU3YjY5NDdkOWQyOTQyM2Y4MGE5Y2JhNTg2NTJjZDI3MTk4NjllNmI4ODliYzNkMmM5MzNhM2ZlZDQxM2EyMzc1OGJlYWI2MTQyMDcwZGRkMzAwM2E3M2U1ZjI1YWQ3OTNkM2FkYzgwMzFkZDM2NDE1ODA3OTQ1ZmE2ODAwYmNkNjIzNjZmNzFlMjA5MDkwOTNjOTRiMWIwMCIsImNpcGhlcmVkT3ZlcmxheUl2IjoiYjAxOTA3ZDNlNmQwYzk4ZDJkNzAxYjdkMzJhZWU3NjYyNmY2OTQzOWNjYmNlMzg0Y2JjNzVlYWY4YzNiZDk4YmE1MDZlZDJkNjM2ZTI0ZjBkMmZjMDlhYzViMjJiZWQzZmQyNWM2YmUwNDY3NzJhNGM4NTVmOWI3NjAzMTU4MzVhOWJlNWZkMjI3NDY4NDRlYjEwMWNiMDc1NjMxNjI2ZWUxNzJlYWU4YzQxZjJkZWIzZGZlNDBjMDllYjY1MTMwYzk2MmVlZDc1MzQxMjQwNzk2M2E1M2YxMGM1NzQ5NzBhM2QzOGI1OWQ0ZWYzODBhNGNmNjZlN2M0ZWQ1ZTlmNiIsImtleUlkIjoxLCJzdHJpY3RNb2RlIjowLCJwZXJzaXN0ZW50IjoiIiwicmVudGFsRHVyYXRpb24iOjAsImZvcmNlTDFUcmFja1R5cGVzIjpudWxsfQ~6nWPenMjyukbOW00BsW8gytdTzf6tyburUc_209IoNQ.video_1444917_2.m3u8?encdomain=cmv1","群发连点器",r"D:\Project\教程\Python全栈0基础入门",False),

# ("https://vip.lz15uu.com/20221116/617_1d8cbf58/1200k/hls/mixed1.m3u8","123"),


        
    ]
    
    # names=[print(name[2],hash_text(name[2]))  for name in lst]
    
    
    
    result=[main(*item) for item in lst]
    
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
