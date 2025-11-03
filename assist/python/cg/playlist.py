import requests

import os
import concurrent.futures


from pathlib import Path



import re
import json
import sys
import asyncio






from base import exception_decorator,logger_helper,except_stack,normal_path,fetch_sync,decrypt_aes_128_from_key,get_folder_path_by_rel,UpdateTimeType,AES_128
from base import download_async,download_sync,move_file,get_homepage_url,is_http_or_https,hash_text,merge_video,convert_video_to_mp4_from_src_dir,convert_video_to_mp4,get_all_files_pathlib,move_file
from base import as_normal,MultiThreadCoroutine,recycle_bin,delete_directory,arabic_numbers,mp4_files
from base import arrange_urls,postfix,codec_base64,codec_base
import pandas as pd


from base import exception_decorator,base64_utf8_to_bytes,bytes_to_base64_utf8

#此文件废弃
def get_real_url(url:str,url_page):
    if is_http_or_https(url) :
        return url
    if url[:1]==r'/':
        return   f"{get_homepage_url(url_page) }{url}"
    else:
        org_path=Path(url_page)
        name=org_path.name
        return url_page.replace(name,url)

from base  import ts_files,move_file


class video_info:
    def __init__(self,url,m3u8_path) -> None:
        self.url=url
        self.method=None
        self.uri=None
        self.iv=None
        self.logger=logger_helper()
        
        content=self.get_m3u8_data(url,m3u8_path)
        self.m3u8=content
        try:
            header=content.split('#EXTINF:')[0].replace(",","\n")

            self.logger.info("内容头",f"\n{header}\n")
        except:
            pass
        # print(content)
        # 正则表达式模式
        self._init_urls(content)
        self._init_keys(content)
    
    
    def get_m3u8_data(self,url,m3u8_path):


        headers = {
  'authority': 'pl-ali.youku.com',
    'accept': '*/*',
    'accept-language': 'zh-CN,zh;q=0.9',
    'origin': 'https://v.youku.com',
    'referer': 'https://v.youku.com/v_show/id_XNzQxNzYyMjA4.html?spm=a2hkn.playlist.myhome.d_1&playMode=pugv',
    'sec-ch-ua': '"Not)A;Brand";v="24", "Chromium";v="116"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.97 Safari/537.36 SE 2.X MetaSr 1.0',
}


        params = {
     'vid': 'XNzQxNzYyMjA4',
    'type': 'flv',
    'ups_client_netip': '240exb8fx3155x3600x9c95x2a7fxf159x7b51',
    'utid': 'ArEsIEQEnkgCAWVd/GueTwU3',
    'ccode': '0502',
    'psid': '4bb2b6261906bacdaf889ba6067e87fb41346',
    'ups_userid': '3760073884',
    'ups_ytid': '3760073884',
    'app_ver': '9.5.101',
    'duration': '1756',
    'expire': '18000',
    'drm_type': '147',
    'drm_device': '7',
    'drm_default': '1',
    'nt': '1',
    'dyt': '1',
    'ups_ts': '1758786419',
    'onOff': '4656',
    'encr': '0',
    'ups_key': 'e4c764494abfe32b523e258e7903974e',
    'ckt': '5',
    'm_onoff': '0',
    'pn': '',
    'app_key': '24679788',
    'drm_type_value': 'default',
    'v': 'v1',
    'bkp': '0',
}



        params = None

        content=None
        if os.path.exists(m3u8_path):
            content=open(m3u8_path,"r",encoding="utf-8-sig").read()
        
        if not content:
            response=response = requests.get(url, params=params, headers=headers)
            self.logger.update_target("解析m3u8",f"{self.url}")
            content=response.text
            
            #写入文件
            if content:
                open(m3u8_path,"w",encoding="utf-8-sig").write(content)
            
            
        return content


    def _init_urls(self,content):
        pattern = re.compile(r'#EXTINF:(.*?),\s*(\S+)\s')

        matches = pattern.findall(content)
        playlist=[]
        for val in matches :
            duration, ts_file =val
            playlist.append([float(duration),get_real_url(ts_file,self.url)])
        
        arrage_lst= arrange_urls(playlist)   
            
        dest_list=[[index,seg["duration"],seg["url"]]    for index,seg in enumerate(arrage_lst) if seg["valid"]]
        
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
        if not key:
            self.logger.error("获取key失败",f"{self.uri}->{url}")

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
    
    
    decry_inst= AES_128(key,iv)
    # def decode():
    #     if not key or  iv is None:
    #         return None 
    #     def _decode(encrypted_data):
    #         return decrypt_aes_128_from_key(key,iv,encrypted_data)
    #     return _decode
    
    #替换为真实的文件头
    headers = {
        'authority': 'v.cdnlz19.com',
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'origin': 'https://lziplayer.com',
        'referer': 'https://lziplayer.com/',
        'sec-ch-ua': '"Not)A;Brand";v="24", "Chromium";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.97 Safari/537.36 SE 2.X MetaSr 1.0',
    }


    async def download(semaphore,args:list|tuple):
        async with semaphore:
            url, temp_path=args
            result=  await download_async(url, temp_path,decry_inst.decrypt,headers=headers) 
            
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
        playlist_logger.trace(multi_thread_coroutine.result)
        
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
        play_logger.update_time(UpdateTimeType.ALL)
        play_logger.info("开始")
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
        with open(os.path.join(root_path, "url", f"{dest_name}-{dest_hash}-lost.json"), "w", encoding="utf-8-sig") as f:
            lost_data = {"count": len(losts),"time":download_time, "data": losts}
            json.dump(lost_data, f, ensure_ascii=False, indent=4)
            
            
    lost_path=[temp_path   for item in losts for _,temp_path in item.items()]  
    success_paths=[item for item in all_path_list if item not in lost_path]
    return lost_count,success_paths
def temp_video_paths_by_count(count,temp_dir,postfix=".mp4"):
    prefix_lst=[f"{index:04}" for index in range(count)]
    return temp_video_paths_by_prefix( prefix_lst,temp_dir,postfix=postfix)


def temp_video_paths_by_prefix(pre_lst:list,temp_dir,postfix=".mp4"):
    return [normal_path(os.path.join(temp_dir, f"{index}{postfix}"))    for index in pre_lst]

def temp_video_paths_by_prefix_index(pre_lst:list[int],temp_dir,postfix=".mp4"):
    prefix_lst=[f"{index:04}" for index in pre_lst ]
    return temp_video_paths_by_prefix( prefix_lst,temp_dir,postfix=postfix)
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

def save_m3u8_data(m3u8_path,data):
    with open(m3u8_path,"w",encoding="utf-8-sig") as f:
        f.write(data)


@exception_decorator()
def get_url_data(url,url_json_path,m3u8_path):
    info=load_url_data(url_json_path)
    
    codec_imp:codec_base=codec_base64()
    
    if not info:
        video=video_info(url,m3u8_path)
        
        
        
        key= video.key
        iv=video.iv

        if key :
            key= codec_imp.encode(key)
        if iv :
            iv= codec_imp.encode(iv)


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
        # org_path= Path(url_json_path).with_suffix(".m3u8")
        # dest_path= org_path.parent.parent / "m3u8" / org_path.name
        # save_m3u8_data(dest_path,video.m3u8)  
    try:    
        key=info.get("key","")
        iv=info.get("iv","")
        if key:
            key=codec_imp.decode(key)
        if iv:
            iv=codec_imp.decode(iv)
        # return None,None,info.get("playlist",[]),info.get("total_len",0)
        return key,iv,info.get("playlist",[]),info.get("total_len",0)
    except:
        return None,None,info.get("playlist",[]),info.get("total_len",0)
        
    
@exception_decorator()
def main(url,dest_name,dest_dir:str=None,force_merge=False):
    root_path=r"F:\worm_practice/player/"
    dest_hash=hash_text(dest_name)
    temp_dir= os.path.join(root_path,"temp",dest_hash) 
    temp_path=normal_path(os.path.join(temp_dir,f"{dest_hash}.mp4")) 
    if not dest_dir:
        dest_dir=os.path.join(root_path,"video") 
    dest_path=normal_path(os.path.join(dest_dir,f"{dest_name}.mp4"))
    
    play_logger= logger_helper("下载",f"{url}->{dest_name}-{dest_hash}")
    play_logger.info("开始")
        
    url_dir=os.path.join(root_path,"url")
    m3u8_dir=os.path.join(root_path,"m3u8")
    
    os.makedirs(dest_dir, exist_ok=True)
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(url_dir, exist_ok=True)
    os.makedirs(m3u8_dir, exist_ok=True)

    #加载已有数据
    cache_name=f"{dest_name}-{dest_hash}"
    
    
    
    
    url_json_path=os.path.join(url_dir,f"{cache_name}.json")
    m3u8_path=os.path.join(m3u8_dir,f"{cache_name}.m3u8")
    
    os.makedirs(os.path.dirname(url_json_path), exist_ok=True)
    os.makedirs(os.path.dirname(m3u8_path), exist_ok=True)
    result=get_url_data(url,url_json_path,m3u8_path)
    if not result:
        play_logger.error("异常",f"获取结果为空：{url}")
        return
    key,iv,info_list,total_len=result
    # key=None
    # url_list=[get_real_url(urls[2],url)  for urls in info_list]

    url_lst_org=[(urls[0],get_real_url(urls[2],url))  for urls in info_list]
    index_lst,url_lst=zip(*url_lst_org)
    
    
    play_logger.info(f"总时长:{total_len}s,共{len(url_lst)}个",update_time_type=UpdateTimeType.STAGE)

    
    temp_path_list=temp_video_paths_by_prefix_index(url_lst,temp_dir,postfix(url_lst[0]))
    
    play_logger.info("开始","下载",update_time_type=UpdateTimeType.STAGE)

    lost_count,success_paths=process_playlist(url_lst, temp_path_list, key, iv, root_path, dest_name, dest_hash)

    # decryp_video(org_path,dest_path,key,iv)
    
    # decryp_videos(url_list,temp_decode_dir,key,iv)
    
    #提前退出,避免合并
    # if lost_count>0 and not force_merge:
    #     return True
    
    # return True
    
    play_logger.info("开始","合并",update_time_type=UpdateTimeType.STAGE)
    merge_video(success_paths,temp_path)
    play_logger.info("完成","合并",update_time_type=UpdateTimeType.STAGE)
    
    move_success= move_file(temp_path,dest_path)
    
    if lost_count==0 and move_success:
        recycle_bin(temp_dir)
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
    recycle_bin(dir_path)
def shut_down(time:10):
    os.system(f"shutdown /s /t {time}")
    
#根据 hash_path.xlsx 中的hash_path(文件夹路径),合并视频文件,参考 hash_path.xlsx 中的name,合并到dest_path
def force_merges():
    raw_df=pd.read_excel(r"F:\worm_practice\player\urls\log_urls.xlsx",index_col=1,sheet_name="原始表")
    already_df=pd.read_excel(r"F:\worm_practice\player\urls\hash_path.xlsx")
    dest_dir=r"F:\worm_practice\player\video"
    
    already_df["hash"]=already_df["hash_path"].apply(lambda x:Path(x).name)
    merge_df=pd.merge(already_df,raw_df,on="hash",how="left")
    print(merge_df)
    
    for index,row in merge_df.iterrows():
        hash_path=row["hash_path"]
        name=row["name"]
        loger=logger_helper(f"合并{row["hash"]}",f"{row["hash_path"]}->{name}")
        loger.info("开始")
        if name:
            force_merge(hash_path,os.path.join(dest_dir,f"{row["name"]}.mp4")) 
            loger.info("完成",update_time_type=UpdateTimeType.ALL)
        else:
            loger.info("失败",f"{hash_path} 没有找到name:{row['hash']}",update_time_type=UpdateTimeType.ALL)
    
    # shut_down(10)
    
#系列视频

def series_movies_info(name:str):
    from base  import json_files,read_from_json_utf8_sig
    lst=[]
    for file in filter(lambda x: name in Path(x).stem, json_files(r"F:\worm_practice\player\urls")):
        if not os.path.exists(file): continue
        if "-lost" in Path(file).stem: 
            os.remove(file)
            continue
        
        json_data=read_from_json_utf8_sig(file)
        if not json_data: continue
        lst.append(json_data)
    lst.sort(key=lambda x:x["name"])
    return lst
    

#播放列表
def series_movies(name:str):
    lst=[]

    for json_data in series_movies_info(name):
        lst.append((json_data["url"],json_data["name"]))
    print(lst)
    
#系列视频合并
def merge_series_movies(name:str):
    collect_dir=None
    logger=logger_helper("合并系列视频",name)
    temp_root=r"F:\worm_practice\player\temp"
    for index,json_data in enumerate(series_movies_info(name)):
        cur_hash=json_data["hash"]

        if not collect_dir: 
            collect_dir=os.path.join(temp_root, cur_hash)

        cur_dir=os.path.join(temp_root, cur_hash)
        recycle_bin(cur_dir)
        continue


        
        from base  import ts_files,move_file
        files=ts_files(cur_dir)
        for file in ts_files(cur_dir):
            cur_path=Path(file)
            new_name=f"{index:03}_{cur_path.name}"
            
            new_path=cur_path.with_name(new_name)
            os.rename(cur_path,new_path)
            
            
            # cur_index=int(cur_path.stem)
            # if cur_index<21 or cur_index+15>len(files):
            #     recycle_bin(str(new_path))
            
            
            continue
            dest_path=os.path.join(collect_dir,new_name)
            # logger.trace(file,dest_path )
            move_file(file,dest_path) 

            
            
        # recycle_bin(cur_dir)
        
        
    return
            
    logger.trace("合并目录",update_time_type=UpdateTimeType.STAGE)
    dest_dir=os.path.join(r"F:\worm_practice\player\video", f"{name}.mp4")
    force_merge(collect_dir,  dest_dir )
    logger.trace("合并视频",update_time_type=UpdateTimeType.STAGE)
    logger.trace("完成",update_time_type=UpdateTimeType.ALL)
#系列视频 单独合并
def series_movies_per_merge(name:str):
    logger=logger_helper("合并系列视频",name)
    temp_root=r"F:\worm_practice\player\temp"
    cache_root=r"F:\worm_practice\player\cache"
    cur_cache_dir=os.path.join(cache_root, name)
    os.makedirs(cur_cache_dir,exist_ok=True)
    temp_dirs=[]
    for index,json_data in enumerate(series_movies_info(name)):
        cur_hash=json_data["hash"]


        cur_dir=os.path.join(temp_root, cur_hash)
        if not os.path.exists(cur_dir):
            continue
        # move_file(cur_dir,cur_cache_dir)
        temp_dirs.append(cur_dir)
        continue

        files=ts_files(cur_dir)
        for file in ts_files(cur_dir):
            cur_path=Path(file)
            new_name=f"{index:03}_{cur_path.name}"
            
            new_path=cur_path.with_name(new_name)
            os.rename(cur_path,new_path)
            
            
            # cur_index=int(cur_path.stem)
            # if cur_index<21 or cur_index+15>len(files):
            #     recycle_bin(str(new_path))
        move_file(cur_dir,cur_cache_dir)
    if not temp_dirs:
        return
    logger.trace("合并目录",update_time_type=UpdateTimeType.STAGE)
    
    
    for index,cur_dir in enumerate(temp_dirs):
        dest_video=os.path.join(r"F:\worm_practice\player\video", f"{name}_{index+1:02}.mp4")
        logger.update_target("合并目录",f"{cur_dir}->{dest_video}")
        force_merge(cur_dir,  dest_video )
        logger.trace("合并视频",update_time_type=UpdateTimeType.STAGE)
        logger.trace("完成",update_time_type=UpdateTimeType.ALL)

def rename_video(org_name:str):
    result = re.sub(
    r'(.*?)第([一二三四五六七八九十]+)季_(\d+)$',
    lambda m: f"{m.group(1)}_第{arabic_numbers(m.group(2))[0]:02}季_{m.group(3)}",
    org_name)
    return result

def rename_videos(file_base_name:str):
    for file in mp4_files(r"F:\worm_practice\player\video"):
        cur_path=Path(file)
        name=cur_path.stem
        if file_base_name not in name: continue
        new_name=rename_video(name)
        if new_name==name: continue
        os.rename(file,cur_path.with_stem(new_name))
        # print(file,cur_path.with_stem(new_name))
    pass
 
def filter_folder(file_base_name:str):
    
    pattern = f"^{file_base_name}" + r'_第(\d{2})季_(\d{2})$'
    
    for file in mp4_files(r"F:\worm_practice\player\video"):
        cur_path=Path(file)
        name=cur_path.stem
        if match := re.match(pattern, name):

            # 解析季数（如01）
            season_num = match.group(1)
            
            # 构建目标目录名称（汪汪队立大功_第01季）
            target_dir = f"{file_base_name}_第{season_num}季"
            dest_dir=cur_path.parent /target_dir
            
            # 创建目录（exist_ok=True表示已存在时不报错）
            os.makedirs(dest_dir, exist_ok=True)
            move_file(file,dest_dir)
    
    pass


#此文件废弃

if __name__=="__main__":

    # filter_folder("汪汪队立大功")
    # rename_videos("汪汪队立大功")
    # exit(0)
    # merge_series_movies("新编蓝猫淘气三千问")
    
    # series_movies_per_merge("爆笑虫子")
    
    # print(arabic_numbers("三千零一十万亿零三千百万零三十"))
    # exit(0)
    # flag="一二三四五六七八"
    # for i in flag:
    #     series_movies_per_merge(f"汪汪队立大功第{i}季")
    # exit(0)
    
    # force_merges()
    # exit(0)
    
    # val=rename_postfix(r"F:\worm_practice\player\temp\46256563\0000.jpeg",".ts")
    # print(val)
    # exit(0)
    # temp_dir=r"F:\worm_practice\player\temp\67f6ba6e"
    # # rename_ts(temp_dir,".jpeg")
    # # exit(0)
    # force_merge(temp_dir,r"F:\worm_practice\player\video\哪吒之魔童闹海.mp4")
    # exit(0)

    
    # temp_dir=r"F:\worm_practice\player\temp\6e94ef53"
    # suffix=[".ts"]
    # # # convert_video_to_mp4_from_src_dir(temp_dir,suffix)

    # temp_path_list=get_all_files_pathlib(temp_dir,suffix)
    # dest_dir=r"F:\worm_practice\player"
    # temp_name="1111.mp4"
    # dest_name="美味姐妹群欢.mp4"
    # temp_path=f"{dest_dir}/{temp_name}"
    # merge_video(temp_path_list,temp_path)
    # move_file(temp_path,f"{dest_dir}/{dest_name}")
    # exit(0)
    
    lst=[


        # ('https://pl-ali.youku.com/playlist/m3u8', 'love_english示范课'),
        ('https://v.cdnlz19.com/20240327/24474_34f63808/2000k/hls/mixed.m3u8', '神奇汉字星球_01'),


        ]

    
    result=[main(*item) for item in lst]
    # shut_down()
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
