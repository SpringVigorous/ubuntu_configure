import os
import requests
import os
import requests
from concurrent.futures import ProcessPoolExecutor
import math
import hashlib
from pathlib import Path 
import sys


root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )



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

        response = requests.head(self.url, headers=self.headers, params=self.params)
        if 'Content-Length' not in response.headers:
            return -1
        
        total_size = int(response.headers['Content-Length'])
        print(f"文件总大小: {total_size} 字节")
        return total_size

class DownloadFile:
    def __init__(self, info:DownloadInfo):
        self.info:DownloadInfo=info
        self.chunk_size=self.info.file_size if self.can_chunk else 0
        self.chunk_count=1
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
    
    def download_chunk(self, start, end, chunk_index):
        chunk_file = self.temp_chunk_path( chunk_index)
        cur_headers = {'Range': f'bytes={start}-{end}'}
        cur_headers.update(self.info.headers)
        print(f"正在下载分块 {chunk_index }: {start}-{end}")
        try:
            response = requests.get(self.info.url, headers=cur_headers, params=self.info.params, stream=True, timeout=600)
            with open(chunk_file, "wb") as f:
                for data in response.iter_content(chunk_size=1024):
                    f.write(data)
            return True
        except Exception as e:
            print(f"下载分块 {chunk_index} 失败: {e}\n删除分块文件{chunk_file}")
            if os.path.exists(chunk_file):
                os.remove(chunk_file)
            return False

    def download(self):

        pass

def temp_chunk_path(temp_dir, chunk_index):
    return os.path.join(temp_dir, f"chunk_{chunk_index}.part")

def download_chunk(url, start, end, chunk_index, temp_dir, params):
    chunk_file = temp_chunk_path(temp_dir, chunk_index)
    cur_headers = {'Range': f'bytes={start}-{end}'}
    print(f"正在下载分块 {chunk_index }: {start}-{end}")
    try:
        response = requests.get(url, headers=cur_headers, params=params, stream=True, timeout=600)
        # response.raise_for_status()


        with open(chunk_file, "wb") as f:
            for data in response.iter_content(chunk_size=1024):
                f.write(data)
        return True
    except Exception as e:
        print(f"下载分块 {chunk_index} 失败: {e}\n删除分块文件{chunk_file}")
        if os.path.exists(chunk_file):
            os.remove(chunk_file)
        return False
def download_file_imp(url, total_size, chunk_size, temp_dir, params):
    results = []
    with ProcessPoolExecutor(20) as executor:
        futures = []
        start = 0
        chunk_index = 0
        while start < total_size:
            end = min(start + chunk_size - 1, total_size - 1)
            if not os.path.exists(temp_chunk_path(temp_dir, chunk_index)):
                futures.append(executor.submit(download_chunk, url, start, end, chunk_index, temp_dir, params))
            start += chunk_size
            chunk_index += 1

        for future in futures:
            results.append(future.result())
    return all(results)


def download_file(url, total_size, chunk_size, temp_dir, params):
    retry_count=1
    while not download_file_imp(url, total_size, chunk_size, temp_dir, params):
        print(f"分块下载失败，第{retry_count}次重试...")
        retry_count+=1

    return True
def download_file_in_chunks(url_info, chunk_count=20, output_file="output.mp4"):
    """
    分块下载文件并保存到本地。
    
    :param url_info: 下载源信息-类型为字典，包含url、headers和params
    :param chunk_count: 分块个数
    :param output_file: 最终保存的文件名
    """
    
    
    # 获取文件的总大小
    url=url_info["url"]
    cur_headers=url_info["headers"]
    params=url_info["params"]

    response = requests.head(url,params=params, headers=cur_headers)
    if 'Content-Length' not in response.headers:
        raise ValueError("无法获取文件大小，服务器可能不支持分块下载。")
    
    total_size = int(response.headers['Content-Length'])
    print(f"文件总大小: {total_size} 字节")
    

    chunk_size=math.ceil(float(total_size)/chunk_count)
    # 创建一个临时文件夹来存储分块文件
   
    curpath=Path(output_file)
    temp_dir = os.path.join(curpath.parent,hashlib.sha256(curpath.name.encode()).hexdigest())
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    if not download_file(url, total_size, chunk_size, temp_dir, params):
        print("分块下载失败")
        return 


    # 合并分块文件
    print("正在合并分块文件...")
    with open(output_file, "wb") as f:
        for i in range(chunk_count):
            chunk_file = os.path.join(temp_dir, f"chunk_{i}.part")
            with open(chunk_file, "rb") as chunk:
                f.write(chunk.read())
            os.remove(chunk_file)  # 删除分块文件

    print(f"文件已成功下载并保存为 {output_file}")

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

    output_file = r"D:\Project\教程\21天课\04_账号定位与账号设置.mp4"

    url_info={
        "url":url,
        "headers":headers,
        "params":params,

    }
    download_file_in_chunks(url_info,chunk_count=20, output_file=output_file)