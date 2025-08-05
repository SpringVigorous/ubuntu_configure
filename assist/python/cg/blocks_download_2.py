import os
import requests
import os
import requests
from concurrent.futures import ThreadPoolExecutor
import math
import hashlib
from pathlib import Path 
import sys
import aiohttp
import asyncio
import os

root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )
from base import as_normal,MultiThreadCoroutine
from base import exception_decorator,logger_helper,except_stack,normal_path,fetch_sync,decrypt_aes_128_from_key,get_folder_path_by_rel,UpdateTimeType


class DownloadInfo:
    def __init__(self, url, headers, params, dest_path):
        self.url = url
        self.headers = headers
        self.params = params
        self.dest_path = dest_path
        self.file_size= self._file_size

    @property
    def temp_dir(self):
        curpath=Path(self.dest_path)
        temp_dir = os.path.join(curpath.parent,hashlib.sha256(curpath.name.encode()).hexdigest())
        os.makedirs(temp_dir, exist_ok=True) 
        return temp_dir

    @property
    def can_chunk(self):
        return self.file_size>0

    @property
    def _file_size(self):
        logger=logger_helper("获取文件大小",self.url)
        response = requests.head(self.url, headers=self.headers, params=self.params)
        if 'Content-Length' not in response.headers:
            logger.warn("失败")
            return -1
        
        total_size = int(response.headers['Content-Length'])
        logger.info("成功",f"文件总大小: {total_size} 字节")
        return total_size

class DownloadFile:
    def __init__(self, info:DownloadInfo):
        self.info:DownloadInfo=info
        self.chunk_size=self.info.file_size if self.can_chunk else 0
        self.chunk_count=1

        self.download_logger=logger_helper("下载文件",self.info.url)
    @property   
    def can_chunk(self):
        return self.info.can_chunk
    def set_chunk_info(self,min_count,max_size): 
        if not self.can_chunk:
            return
        total_size = self.info.file_size

        chunk_count=min_count
        chunk_size=math.ceil(total_size/chunk_count)
        if chunk_size>max_size:
            chunk_size=max_size
            chunk_count=math.ceil(total_size/chunk_size)

        self.chunk_count=chunk_count
        self.chunk_size=chunk_size
    def chunks(self):
        if not self.can_chunk:
            return []

        results=[]  

        for i in range(self.chunk_count):
            start=i*self.chunk_size
            end = min(start+self.chunk_size , self.info.file_size )- 1
            results.append((start,end))

        return results
    def temp_chunk_path(self,chunk_index):
        return os.path.join(self.info.temp_dir, f"chunk_{chunk_index}.part")
    



    async def download_chunk(self, start, end, chunk_index):
        chunk_file = self.temp_chunk_path(chunk_index)
        cur_headers = {'Range': f'bytes={start}-{end}'}
        cur_headers.update(self.info.headers)
        self.download_logger.info(f"正在下载分块 {chunk_index}: {start}-{end}")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.info.url, headers=cur_headers, params=self.info.params) as response:
                    # if response.status == 200:
                    if response.ok:
                        with open(chunk_file, "wb") as f:
                            while True:
                                chunk = await response.content.read(1024)
                                if not chunk:
                                    break
                                f.write(chunk)
                        return True
                    else:
                        self.download_logger.info(f"下载分块 {chunk_index} 失败: HTTP 状态码 {response.status}")
                        return False
        except Exception as e:
            self.download_logger.info(f"下载分块 {chunk_index} 失败: {e}\n删除分块文件 {chunk_file}")
            if os.path.exists(chunk_file):
                os.remove(chunk_file)
            return False

    def download(self):

        if not self.download_file(): 
            return
        self.merge_chunks()



    def download_file_imp(self):

        async def download_impl(semaphore,args:tuple):
            async with semaphore:
                start,end,chunk_index=args
                result=  await self.download_chunk(start,end,chunk_index)

                return result

        lst=[]  
        for chunk_index,chunk_info in enumerate(self.chunks()):
            start, end=chunk_info
            if not os.path.exists(self.temp_chunk_path(chunk_index)):
                lst.append((start,end,chunk_index))

        multi_thread_coroutine = MultiThreadCoroutine(download_impl,lst)
        try:
            asyncio.run(multi_thread_coroutine.run_tasks()) 
            success=multi_thread_coroutine.success
            if not success:
                info=[multi_thread_coroutine.fail_infos,except_stack()]
                info_str="\n".join(info)
                self.download_logger.error("异常",f"\n{info_str}\n",update_time_type=UpdateTimeType.ALL)
            self.download_logger.info(multi_thread_coroutine.result)
        except Exception as e:
            self.download_logger.error("下载异常",except_stack(),update_time_type=UpdateTimeType.ALL)
            return False



    def download_file(self):
        retry_count=1
        while not self.download_file_imp():
            self.download_logger.info(f"分块下载失败，第{retry_count}次重试...")
            retry_count+=1

        return True
    def merge_chunks(self):

        output_file=self.info.dest_path
        self.download_logger.info(f"正在合并分块，保存到{output_file}")

        # 合并分块文件
        self.download_logger.info("正在合并分块文件...")
        with open(output_file, "wb") as f:
            for i in range(self.chunk_count):
                
                chunk_file = self.temp_chunk_path(i)
                with open(chunk_file, "rb") as chunk:
                    f.write(chunk.read())
                os.remove(chunk_file)  # 删除分块文件

        self.download_logger.info(f"文件已成功下载并保存为 {output_file}")




    

if __name__ == "__main__":


    import requests

    headers = {
        'authority': 'v11.talk-fun.com',
        'sec-ch-ua': '";Not A Brand";v="99", "Chromium";v="94"',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 SE 2.X MetaSr 1.0',
        'sec-ch-ua-platform': '"Windows"',
        'accept': '*/*',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-dest': 'video',
        'accept-language': 'zh-CN,zh;q=0.9',
        'range': 'bytes=0-',
    }

    params = {
        'sign': '1738466952-20250201112912-4223483158-4fa1a645af7d7d3d0c412d3fc80bb479',
        'auth_key': '1738466952-0-0-295361a27ad55d43f10679ad97deffd2',
        'pid': '62307',
        'limit': '146K',
        'cdt': '1734691238',
        'part': '1',
        'from': 'tfvod',
    }


    url='https://v11.talk-fun.com/7/video/ba/ce/f6/5d97274454d630d7907984c396/3a148d10_video.mp4'

    output_file = r"F:\教程\短视频教程\抖音\21天课\00004_账号定位与账号设置.mp4"

    info=DownloadInfo(url,headers,params,output_file)
    file=DownloadFile(info)
    file.set_chunk_info(20,1024*1024*20)
    file.download()
