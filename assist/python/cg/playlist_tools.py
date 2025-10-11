import requests

import os
import concurrent.futures


from pathlib import Path



import re
import json
import sys
import asyncio






from base import exception_decorator,logger_helper,except_stack,normal_path,fetch_sync,decrypt_aes_128_from_key,get_folder_path_by_rel,UpdateTimeType
from base import download_async,download_sync,move_file,get_homepage_url,is_http_or_https,hash_text,delete_directory,merge_video,convert_video_to_mp4_from_src_dir,convert_video_to_mp4,get_all_files_pathlib,move_file
from base import as_normal,MultiThreadCoroutine
from base import arrange_urls,postfix
import pandas as pd


from base import exception_decorator,base64_utf8_to_bytes,bytes_to_base64_utf8,ThreadPool,AES_128
from concurrent.futures import ThreadPoolExecutor
from playlist_kernel import *


@exception_decorator()
def handle_playlist_async(url_list,temp_paths,key,iv):
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

#同步方式下载
@exception_decorator()
def handle_playlist(url_list,temp_paths,key,iv):
    if not url_list or not temp_paths:
        return False
    

    playlist_logger= logger_helper("下载文件",Path(temp_paths[0]).parent)

    playlist_logger.trace("开始")
    decry_inst= AES_128(key,iv)
    
    #替换为真实的文件头
    headers = {
        'authority': 'v.cdnlz19.com',
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'origin': 'https://v.youku.com',
        'referer': 'https://v.youku.com',
        'sec-ch-ua': '"Not)A;Brand";v="24", "Chromium";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.97 Safari/537.36 SE 2.X MetaSr 1.0',
    }


    lst=[(url,path) for url,path in zip(url_list,temp_paths) if not os.path.exists(path) ]


        
    results={}
    # 使用 ThreadPoolExecutor 创建线程池，max_workers 指定最大线程数
    with ThreadPoolExecutor(max_workers=10) as executor:
        # 使用 submit 方法将任务提交到线程池，返回 Future 对象
        future_to_url = {executor.submit(download_sync,url,path,decry_inst.decrypt,headers=headers):url for url,path in lst}
        # 使用 as_completed 获取已完成的任务结果
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            data=False
            try:
                data = future.result()  # 获取任务返回值，如果发生异常会在这里抛出

            except Exception as e:
                playlist_logger.error("异常",f"下载{url}失败: {e}")
            results[url]=data

    return  all([item for key,item in results.items()])



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
        play_logger.debug("开始", update_time_type=UpdateTimeType.ALL)
        success = handle_playlist(urls, temp_paths, key, iv)
        play_logger.debug("完成", update_time_type=UpdateTimeType.ALL)
        download_time+=1
        
        #检查下载情况
        if success:
            play_logger.debug("统计",f"下载完毕，已下载{all_count}/{all_count}个",update_time_type=UpdateTimeType.ALL)
            return 0,all_path_list
        else:
            losts = []

            for url,temp_path in  zip(urls,temp_paths):
                if not os.path.exists(temp_path):
                    losts.append({"url":url,"path":temp_path})
                else:
                    success_paths.append(temp_path)
            lost_count = len(losts)
            play_logger.debug("统计",f"已下载{all_count-lost_count}个,缺失{lost_count}个",update_time_type=UpdateTimeType.ALL)
                
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
def main(url,dest_name,dest_dir:str=None,force_merge=False):
    root_path=r"F:\worm_practice/player/"
    dest_hash=hash_text(dest_name)
    temp_dir= os.path.join(root_path,"temp",dest_hash) 
    temp_path=normal_path(os.path.join(temp_dir,f"{dest_hash}.mp4")) 
    dest_path=normal_path(os.path.join(root_path,"video",f"{dest_name}.mp4")) if not dest_dir else normal_path(os.path.join(dest_dir,f"{dest_name}.mp4"))
    
    play_logger= logger_helper("下载",f"{url}->{dest_name}-{dest_hash}")
    play_logger.debug("开始")
        
    os.makedirs(temp_dir, exist_ok=True)
    
    #加载已有数据
    cache_name=f"{dest_name}-{dest_hash}"
    
    url_json_path=os.path.join(root_path,"urls",f"{cache_name}.json")
    m3u8_path=os.path.join(root_path,"m3u8",f"{cache_name}.m3u8")
    key,iv,info_list,total_len=get_url_data(url,url_json_path,m3u8_path)
    # key=None
    # url_list=[get_real_url(urls[2],url)  for urls in info_list]
    url_list=[get_real_url(urls[2],url)  for urls in info_list]
    play_logger.debug(f"总时长:{total_len}s,共{len(url_list)}个",update_time_type=UpdateTimeType.STAGE)

    
    temp_path_list=temp_video_paths(len(url_list),temp_dir,postfix(url_list[0]))
    
    play_logger.debug("开始","下载",update_time_type=UpdateTimeType.STAGE)

    lost_count,success_paths=process_playlist(url_list, temp_path_list, key, iv, root_path, dest_name, dest_hash)

    # decryp_video(org_path,dest_path,key,iv)
    
    # decryp_videos(url_list,temp_decode_dir,key,iv)
    
    #提前退出,避免合并
    # if lost_count>0 and not force_merge:
    #     return True
    
    # return True
    
    play_logger.debug("开始","合并",update_time_type=UpdateTimeType.STAGE)
    merge_video(success_paths,temp_path)
    play_logger.debug("完成","合并",update_time_type=UpdateTimeType.STAGE)
    
    move_file(temp_path,dest_path)
    
    if lost_count==0 and False:
        delete_directory(temp_dir)
        play_logger.debug("完成" ,update_time_type=UpdateTimeType.ALL)
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
        loger.debug("开始")
        if name:
            force_merge(hash_path,os.path.join(dest_dir,f"{row["name"]}.mp4")) 
            loger.debug("完成",update_time_type=UpdateTimeType.ALL)
        else:
            loger.debug("失败",f"{hash_path} 没有找到name:{row['hash']}",update_time_type=UpdateTimeType.ALL)
    
    # shut_down(10)
    
def split_info_to_srt(url_json_path:str,temp_dir:str,dest_srt_path:str):
    from base import json_files,read_from_json_utf8_sig,ts_files
    from pathlib import Path
    json_data=read_from_json_utf8_sig(url_json_path)
    if not  json_data: return
    datas=json_data["playlist"]
    json_result=[{"name":data[0],"duration":data[1]} for data in datas if data and len(data)>1]
    
    ts_result=[{"name":int(Path(ts_file).stem)} for ts_file in ts_files(temp_dir)]
    
    json_df=pd.DataFrame(json_result)
    ts_df=pd.DataFrame(ts_result)
    result_df=pd.merge(ts_df,json_df,on="name",how="left")
    result_df["diff"]=result_df["name"].diff().fillna(5).astype(int)
    result_df["time"]=result_df["duration"].cumsum()
    mask=result_df["diff"]>1
    
    sub_dir=Path(temp_dir).stem
    
    pic_cache_dir=os.path.abspath(os.path.join(url_json_path,"../../pic",sub_dir))
    os.makedirs(pic_cache_dir, exist_ok=True)
    names=result_df.loc[mask,"name"].to_list()
    from base import cover_video_pic
    for i,name in enumerate(names):
        ts_path=os.path.join(temp_dir,f"{name:04}.ts")
        cover_path=os.path.join(pic_cache_dir,f"{i+1:04}.jpg")
        cover_video_pic(ts_path,cover_path)
    return
    
    pre_mask=mask.shift(-1,fill_value=True)
    dest=result_df[pre_mask]
    
    dest_df=pd.DataFrame()
    spec_time_lst=[0]
    spec_time_lst.extend(result_df.loc[pre_mask,"time"].values)
    results=[]
    for i in range(len(spec_time_lst)-1):
        start_time=int(spec_time_lst[i])
        end_time=int(spec_time_lst[i+1])
        results.append((start_time,end_time,f"{i+1:03}"))
    from base import generate_srt
    generate_srt(results,dest_srt_path,"s")
    
    return
    dest_df["spec_time"]=spec_time_lst
    dest_df["per_time"]=dest_df["spec_time"].diff().fillna(0).astype(int)

    per_time_lst=dest_df["per_time"].values.tolist()
    per_time_lst.remove(len(per_time_lst)-1)
    
    # result_df.loc[pre_mask,"总时长"]=result_df.loc[pre_mask,"time"]
    dest_df.to_excel(f"{url_json_path}.xlsx")
    
    
    pass
 
if __name__=="__main__":
    split_info_to_srt(r"F:\worm_practice\player\urls\《爆笑虫子_第一季》HD中字高清资源免费在线观看_动画片_555电影网-3a7c8a7f.json",
               r"F:\worm_practice\player\temp\3a7c8a7f",
               r"F:\worm_practice\player\video\爆笑虫子_01.srt")
    pass