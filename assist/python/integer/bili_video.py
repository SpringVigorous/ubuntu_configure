import requests
from urllib.parse import quote
import re
import json
from pprint import pprint 
import sys
import subprocess
from concurrent.futures  import ThreadPoolExecutor
import os
import asyncio
import aiohttp

from collections import namedtuple, OrderedDict
from queue import Queue

from lxml import etree
import __init__
from base.com_log import logger as logger
from base.string_tools import sanitize_filename,cur_date_str
from base.file_tools import read_write_async,read_write_sync
from base.path_tools import normal_path
import glob


global_temp_dir=os.path.join(os.getcwd(), "temp") 
os.mkdir(global_temp_dir) if not os.path.exists(global_temp_dir) else None
def ffmpeg_path():
    # 获取环境变量 PATH 的值
    path_dirs = os.environ['PATH'].split(os.pathsep)

    # 遍历 PATH 中的每个目录
    for path_dir in path_dirs:
        # 构造 ffmpeg.exe 的模式匹配路径
        ffmpeg_pattern = os.path.join(path_dir, 'ffmpeg.exe')
        # 使用 glob 模块搜索 ffmpeg.exe
        ffmpeg_paths = glob.glob(ffmpeg_pattern)
        if ffmpeg_paths:
            return normal_path(ffmpeg_paths[0]) 
        
class MergeMedia:
    params_queue=Queue(100)

    def __init__(self):    
        pass  
    
    @staticmethod
    async def add_params(video_path,audio_path,dest_path):
        MergeMedia.params_queue.put((video_path,audio_path,dest_path))
    
    @staticmethod
    async def merge_media(video_path,audio_path,dest_path):
        await MergeMedia.add_params(video_path,audio_path,dest_path)
        while not MergeMedia.params_queue.empty():
            item = MergeMedia.params_queue.get()
            if item is None:
                continue
            video_path,audio_path,dest_path=item
            logger.trace(f"准备合并：{video_path}和{audio_path}->{dest_path}")  
            out_info, err_info ,return_code = await merge_audio_mp4(video_path,audio_path,dest_path) 
            logger.trace(f"合并完成：{video_path}和{audio_path}->{dest_path};out_info:{out_info},err_info:{err_info},return_code:{return_code}")  
            
            
            
            
#路径中不能出现汉字，否则ffmpeg会报错
async def merge_audio_mp4(video_path,audio_path,dest_path):
    
    
    # 合并可以from moviepy.editor import *导入这个模块
    
    
    # cmd=f'ffmpeg -hide_banner -i "{video_path}" -i "{audio_path}" -c:v copy -c:a aac -strict experimental "{dest_path}"'
    # subprocess.run(cmd)
    
    # D:\Tool\ffmpeg\bin\ffmpeg.exe -hide_banner -i "F:\教程\哔哩哔哩\双笙子佯谬\现代C++项目实战\cache\3_【C++项目实战】实现一个JSON解析器.mp4" -i "F:\教程\哔哩哔哩\双笙子佯谬\现代C++项目实战\cache\3_【C++项目实战】实现一个JSON解析器.mp3" -c:v copy -c:a aac -strict experimental "F:\教程\哔哩哔哩\双笙子佯谬\现代C++项目实战\dest\3_【C++项目实战】实现一个JSON解析器.mp4"
    
    exe_path=ffmpeg_path()
    args=[
        '-hide_banner',
        '-i',
        video_path,
        '-i',
        audio_path,
        '-c:v',
        'copy',
        '-c:a',
        'aac',
        '-strict',
        'experimental',
        dest_path
        ]
    
    
    info=f"运行外部程序：{exe_path} {' '.join(args)}"
    logger.trace(f"开始{info}")
    try:
        # 创建子进程
        process = await asyncio.create_subprocess_exec(
            exe_path, *args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # 读取标准输出和标准错误
        stdout, stderr = await process.communicate()

        # 等待进程完成
        return_code = await process.wait()
        
        code_info="成功" if return_code==0 else f"失败，返回码：{return_code}"
        logger.info(f"{code_info},详情：{info}")

        # 返回结果
        return stdout.decode(), stderr.decode(), return_code
    except Exception as e:
        logger.error(f"失败{info}，Error running external exe: {e}")
        return None, None, None

MideaInfo=namedtuple("MideaInfo",["bvid","title"])

class CatalogInfo:
    
    def __init__(self,author_name:str="",collection_name:str="",mideas:list=[],org_data=None,author_id:str="",collection_id:str="",cur_bvid:str=""):
        self.author_name=author_name
        self.collection_name=collection_name
        self.mideas=mideas
        self.org_data=org_data
        self.author_id=author_id
        self.collection_id=collection_id

# CatalogInfo=namedtuple("catalogInfo",["author_name","collection_name","bvids","org_data","author_id","collection_id","cur_bvid"])

def logout_info(data,info:CatalogInfo):
    pages=data["pages"]
    page_count=len(pages)
    
    tittle=data["title"]
    info.collection_name=sanitize_filename(tittle)
    info.collection_id=str(data["duration"])

    info.mideas=[MideaInfo(bvid,item["part"])  for item in pages ]
    
def login_info(data,info:CatalogInfo):
    pages=data["pages"]
    page_count=len(pages)
    
    
    catalogs=data["ugc_season"]

    info.collection_name=sanitize_filename(catalogs["title"])
    
    # count=catalogs["ep_count"]
    sections=catalogs["sections"]

    info.collection_id=str(data["season_id"])

    info.mideas=[ item for sec in sections for item in map(lambda x:MideaInfo(x["bvid"], sanitize_filename(x["title"])),sec["episodes"])]

def  get_catalog(url,headers,params):
        with requests.get(url,headers=headers,params=params) as response:
            # "author_name","collection_name","bvids","org_data","autor_id","collection_id","cur_bvid"
            info= CatalogInfo()
            
            response.encoding='utf-8'
            org_data=response.text

            data=json.loads(org_data)["data"]["View"]
            info.cur_bvid=data["bvid"]
            
            author=data["owner"]
            info.author_name=sanitize_filename(author["name"])      
            info.author_id=str(author['mid'])
            info.org_data=org_data
            is_logout=not "ugc_season" in data
            try:
                if is_logout:
                    logout_info(data,info)
                else:
                    login_info(data,info)
            except: 
                file_name=f"{cur_date_str()}_{params["bvid"]}_catalog.json"
                file_path=os.path.join(global_temp_dir,file_name)
                read_write_sync(org_data,file_path,"w",encoding="utf-8") 
                logger.error(f"解析失败：输出中间数据到文件{file_path}")   
                #直接退出，避免异常
                os._exit(1)
            
            
            return  info

        

async def fetch_data(url,headers, session, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            async with session.get(url,headers=headers) as response:
                if response.status == 200:
                    content_length = int(response.headers.get('Content-Length', 0))
                    received_data = await response.read()
                    if len(received_data) == content_length:
                        return received_data
                    else:
                        raise aiohttp.ClientError(
                            response.status,
                            "Not enough data for satisfy content length header."
                        )
                else:
                    raise Exception(f"HTTP error: {response.status}")
        except aiohttp.ClientError as e:
            print(f"{retries} times,Request failed: {e}")
            retries += 1
            await asyncio.sleep(5)  # 等待 5 秒后重试
    return None
    # raise Exception("Max retries exceeded")



        
async def async_download(url,headers,dest_path):
    logger.info(f"开始下载文件：{url} -> {dest_path}")
    
    
    async with aiohttp.ClientSession() as session:
        content=await fetch_data(url,headers,session,5)
        if not content:
            logger.error(f"下载文件失败：{url} -> {dest_path}")
            return False
        
        # async with session.get(url,headers=headers) as response:
        #     content=await response.read()
            
        await read_write_async(content,dest_path,mode="wb")
        
            # async with  aiofiles.open(dest_path,"wb") as f:
            #     content= await response.read()
            #     await f.write(response.content)
    logger.info(f"下载文件已完成：{url} -> {dest_path}")
    return True
      

def result_name(num:int,title:str,index:int=0): 
    result=f"{num}"
    if title:
        result=f"{result}_{title}"
    if index>0:
        result=f"{result}_{index}"
      
    return result   



async def handle_video(num,bvid,title,header,cache_dir,html_dir,merge_dir,dest_dir,merge_list=None,cache_list=None):


    
    # page_url=f"https://www.bilibili.com/video/{bvid}/?spm_id_from=333.999.0.0"
    page_url=f"https://www.bilibili.com/video/{bvid}/?p={num}&spm_id_from=333.999.0.0"
    # page_url=f"https://www.bilibili.com/video/{bvid}/?p={num}"n
    
    async with aiohttp.ClientSession() as session:
    
        async with session.get(page_url,headers=header) as response:  
            content= await response.text(encoding='utf-8')

            
            # <h1 data-title="" />
            # html= etree.HTML(content)
            # titles=html.xpath('//h1[@data-title]/@data-title')
            
            # title=sanitize_filename(titles[0]) if len(titles)>0 else "无标题"
            logger.debug(f"num:{num},cur_title:{title},page_url:{page_url}")
            
            datas=re.findall(r'<script>window.__playinfo__=(.*?)</script>',content,re.S)
            if not datas:
                temp_path=os.path.join(html_dir,f"{num}_temp.html")
                logger.error(f"num:{num},cur_title:{title},page_url:{page_url} 没有找到播放信息\t输出临时文件：{temp_path}")
                await read_write_async(content,temp_path,"w",encoding="utf-8")
                return
               
             
            for index ,item in enumerate(datas) :
               
                logger.debug(f"title_type:{type(title)},cur_title:{title},page_url:{page_url},index:{index}")
                name=result_name(num,"",index)
                dest_name=result_name(num,title,index)
                mp4_name=f"{name}.mp4"
                mp3_name=f"{name}.mp3"
                
                dest_mp4_name=f"{dest_name}.mp4"
                merge_path=normal_path(os.path.join(merge_dir,mp4_name))
                dest_path=normal_path(os.path.join(dest_dir,dest_mp4_name))
                
                #检查是否已存在
                if dest_mp4_name in merge_list:
                    logger.info(f"跳过已存在文件：{dest_path}")
                    continue
                if  not mp4_name in merge_list:
                    audio_path=normal_path(os.path.join(cache_dir,mp3_name)) 
                    video_path=normal_path(os.path.join(cache_dir,mp4_name))

                    dict=json.loads(item)
                    # pprint(dict)
                    video_url=dict['data']['dash']['video'][0]['baseUrl']
                    audio_url=dict['data']['dash']['audio'][0]['baseUrl']
                    tasks=[]
                    if  not mp3_name in cache_list:
                        tasks.append(asyncio.create_task(async_download(audio_url,header,audio_path)))
                    else:
                        logger.info(f"跳过已存在缓存文件：{audio_path}")
                        
                    if not mp4_name in cache_list:
                        tasks.append(asyncio.create_task(async_download(video_url,header,video_path)))
                    else:
                        logger.info(f"跳过已存在缓存文件：{video_path}")
                        
                    if  len(tasks)>0:
                        if index<1:
                            cur_obj=read_write_async(content,os.path.join(html_dir,f"{dest_name}.html"),"w",encoding="utf-8") 
                            tasks.append(asyncio.create_task(cur_obj))
                        # logger.trace(f"正在临时文件下载：{video_path},{audio_path}")  
                        result= await asyncio.gather(*tasks)
                        if not all(result):
                            logger.error(f"下载文件失败：{video_path},{audio_path},results:{result}")
                            continue
                        
                        logger.trace(f"临时文件下载完成：{video_path},{audio_path}")  
                    
                    
                    # 合并可以from moviepy.editor import *导入这个模块
                    # cmd=f"ffmpeg -hide_banner -i {video_path} -i {audio_path} -c:v copy -c:a aac -strict experimental {dest_path}"
                    # subprocess.run(cmd)
                    
                    await MergeMedia.merge_media(video_path,audio_path,merge_path) 
  
                
                    # 重命名文件
                    logger.info(f"准备文件重命名：{merge_path} -> {dest_path}")
                    os.rename(merge_path,dest_path)
                    logger.info(f"完成文件重命名：{merge_path} -> {dest_path}")
                
                

def list_files(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            # file_path = os.path.join(root, file)
            file_path =  file
            file_list.append(file_path)
    return file_list
            
class BiliVideoSet:
    header={
        "Cookie":"buvid3=E91C935D-D64B-7079-EE9F-AB64970D842548554infoc; b_nut=1705554648; CURRENT_FNVAL=4048; _uuid=142361024-310E3-FEFC-5568-10C103AA1223DE48383infoc; buvid4=0C33E73C-6A84-68AD-BEA9-5F5E545A16D349445-024011805-4X7VBkL4YUEM3E0X%2F3qFeZqkTb4HnmJ2vy1qT%2FRJICjhDQ%2FVZL32GFpXMcEme29h; rpdid=0zbfVGcJRV|37D2B6kr|4kK|3w1RqkFY; enable_web_push=DISABLE; header_theme_version=CLOSE; home_feed_column=5; browser_resolution=2560-1279; CURRENT_QUALITY=80; buvid_fp_plain=undefined; fingerprint=90c499da9942bd53c5bb74bd199ee4c1; PVID=1; buvid_fp=90c499da9942bd53c5bb74bd199ee4c1; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjQyNDI4NTAsImlhdCI6MTcyMzk4MzU5MCwicGx0IjotMX0.041kkccOZCoBn7bJ-i9u32vRfb2yXqSye5K9w0uusFI; bili_ticket_expires=1724242790; b_lsid=F1110AA55_19168D04C84; bp_t_offset_622817009=967241959502512128; SESSDATA=b06f5c67%2C1739594054%2Cdb3dd%2A81CjA_-1P8v8Q2gLWoxpnyrQBA8Q2ytyBYb9ekcGirgW-oXXknPEQmnWgGMSpYTDiyD_0SVlEtM2gyS0RlY01sdEpkaFVibEwybnlJa0NkUFpWam96RGJ3T0lWN1ltbzUzZ0EzU19lU3c4Q2xTUmg4TEhkSlAtWHV6MXktZFFBUGxqWGdRVzBLb1pRIIEC; bili_jct=19961afc7cd296a69e37620d58248360; DedeUserID=622817009; DedeUserID__ckMd5=f6c2c5f50f5785dd; sid=7c3tw0d0",
        'Origin':'https://www.bilibili.com',
        'Referer':'https://www.bilibili.com/',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',   
    }
    list_url="https://api.bilibili.com/x/web-interface/wbi/view/detail"
    proxies={
        
        
    }

    def __init__(self,bvid,base_dir,buffer_dir) -> None:
        self.base_dir=base_dir
        data={
        'platform':'web',
        'bvid':bvid,
        'aid':'1106031994',
        'w_rid':'fce2c75e987084e0d17524301290024c',
        'wts':'1724037685',
        }
        catalog=get_catalog(BiliVideoSet.list_url,headers=BiliVideoSet.header,params=data)
        author_name=catalog.author_name
        collection_name=catalog.collection_name
        bvids=catalog.mideas
        self.bvids=[item.bvid for item in bvids]
        self.titles=[item.title for item in bvids]
        self.org_data=catalog.org_data
        author_id=catalog.author_id
        collection_id=catalog.collection_id

        self.dest_dir=os.path.join(base_dir,author_name,collection_name)
        temp_dir=os.path.join(buffer_dir,author_id,collection_id)
        logger.info(f"当前缓存根目录：{temp_dir}")
        
        os.makedirs(temp_dir,exist_ok=True)
        self.html_dir=os.path.join(temp_dir,"html",cur_date_str())
        self.merge_dir=os.path.join(temp_dir,"dest")
        self.cache_dir=os.path.join(temp_dir,"cache")
        

        # self.dest_dir=os.path.join(self.cur_dir,"dest")
        
        os.makedirs(self.dest_dir,exist_ok=True)
        os.makedirs(self.html_dir,exist_ok=True)
        os.makedirs(self.merge_dir,exist_ok=True)
        os.makedirs(self.cache_dir,exist_ok=True)
        
        dest_alreadys=[list_files(self.dest_dir),list_files(self.dest_dir)]
        dests=[item for items in dest_alreadys for item in items ]
        self.dest_alreadys=list(OrderedDict.fromkeys(dests))

        self.cache_alreadys=list_files(self.cache_dir)
        
    @property
    def count(self):
        return len(self.bvids)
    
    
    def bvid(self,index):
        return self.bvids[index] if index<self.count else ""
    def title(self,index):
        return self.titles[index] if index<self.count else ""
        
    async def handle_vidios(self, batch_size=5):

        # #写入文件
        # tasks=[asyncio.create_task(read_write_async(self.org_data,os.path.join(self.html_dir,f"0_{self.title}.json"),mode="w",encoding="utf-8"))]
        # #异步操作
        # for num in range(self.count):
        # # for num in range(2,3):
        #     tasks.append(asyncio.create_task(handle_vidio(num+1,self.bvid(num),self.title(num), BiliVideoSet.header,self.cache_dir,self.html_dir,self.merge_dir,self.dest_dir, self.dest_alreadys,self.cache_alreadys)))
        # await asyncio.wait(tasks)  
        
        semaphore = asyncio.Semaphore(batch_size)  # 控制并发数量为 10

        async def run_with_semaphore(task):
            async with semaphore:
                await task
        read_write_sync(
            self.org_data,
            os.path.join(self.html_dir, f"0_{self.title}.json"),
            mode="w",
            encoding="utf-8"
        )
        # tasks = []

        # # 添加初始任务
        # tasks.append(asyncio.create_task(run_with_semaphore(read_write_async(
        #     self.org_data,
        #     os.path.join(self.html_dir, f"0_{self.title}.json"),
        #     mode="w",
        #     encoding="utf-8"
        # ))))
        count =self.count
        # 分批提交任务
        for i in range(0, count, batch_size):
            batch_tasks = []
            for num in range(i, min(i + batch_size, count)):
                batch_tasks.append(asyncio.create_task(run_with_semaphore(
                    handle_video(
                        num + 1,
                        self.bvid(num),
                        self.title(num),
                        BiliVideoSet.header,
                        self.cache_dir,
                        self.html_dir,
                        self.merge_dir,
                        self.dest_dir,
                        self.dest_alreadys,
                        self.cache_alreadys
                    )
                )))
            await asyncio.wait(batch_tasks)

        # await asyncio.wait(tasks)


if __name__=="__main__":
    # bvid="BV1Ur4y1V7Kh"
    bvid="BV1tLH7eGEqB"
    cur_dir=r"F:\教程\哔哩哔哩"
    temp_dir="F:/cache/bilibili"
    collection= BiliVideoSet(bvid,cur_dir,temp_dir)
    
    asyncio.run(collection.handle_vidios(os.cpu_count()))


