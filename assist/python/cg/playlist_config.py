import os
from base import hash_text,normal_path,sanitize_filename,read_from_json_utf8_sig,write_to_json_utf8_sig
import re
from playlist_kernel import *


root_path=r"F:\worm_practice/player/"
root_temp_dir= os.path.join(root_path,"temp")
video_dir= os.path.join(root_path,"video")
url_dir= os.path.join(root_path,"urls")
m3u8_dir= os.path.join(root_path,"m3u8")
video_xlsx= os.path.join(root_path,"video.xlsx")


os.makedirs(root_temp_dir,exist_ok=True)
os.makedirs(video_dir,exist_ok=True)
os.makedirs(url_dir,exist_ok=True)
os.makedirs(m3u8_dir,exist_ok=True)

def video_hash_name(video_name:str):
    return hash_text(video_name)
def dest_video_path(video_name:str):
    return  os.path.join(video_dir,f"{video_name}.mp4")
def temp_video_dir(video_name:str):
    cur_dir=os.path.join(root_temp_dir,video_hash_name(video_name))
    os.makedirs(cur_dir,exist_ok=True)
    return  cur_dir


def url_json_path(vieo_name:str):
    return os.path.join(url_dir,f"{cache_name(vieo_name)}.json")

def m3u8_path(vieo_name:str):
    return os.path.join(m3u8_dir,f"{cache_name(vieo_name)}.m3u8")

def cache_name(video_name:str):
    return f"{video_name}-{video_hash_name(video_name)}"

listent_shop_api=["hls/index.m3u8","hls/mixed.m3u8","index.m3u8","master.m3u8","*/master.m3u8*","mixed.m3u8"]
# 
# listent_shop_api=["*/index.m3u8"]

url_id="url"
m3u8_url_id="m3u8_url"
m3u8_hash_id="m3u8_hash"
video_title_id="title"
video_name_id=video_title_id
hash_id="hash"
download_status_id="download"

video_sheet_name="video"


class VideoUrlInfo:
    def __init__(self,title:str=None,url:str=None,m3u8_url:str=None,download:int=-1,m3u8_hash:str=None):
        self._title:str=title
        self._url=url
        self._m3u8_url=m3u8_url
        self._download=download
        self._m3u8_hash:str=m3u8_hash
        self._info:video_info=None

    def fetch_m3u8_data(self):
        pass
        
    @property
    def info(self)->video_info:
        if self._info:
            return self._info
        if self.exist_m3u8_path:
            self._info=video_info(self.m3u8_url,self.m3u8_path)
            return self._info
    
    @property
    def m3u8_hash(self)->str:
        if self._m3u8_hash:
            return self._m3u8_hash
        if self.info:
            self._m3u8_hash=self.info.m3u8_hash
            return self._m3u8_hash
    
    @property
    def has_raw_url(self)->bool:
        return bool(self._url)
    @property
    def has_m3u8_url(self)->bool:
        return bool(self._m3u8_url)
    @property
    def has_download(self)->bool:
        return self._download>=0
    @property
    def title(self)->str:
        
        name=self._title
        if not name:
            return ""
        if "《" in name and "》" in name:
            pattern = r'《([^《》]+)》'
            match = re.search(pattern, name)
            if match:
                name=match.group(1)


        return sanitize_filename(name).replace("-","_")


    @property
    def url(self)->str:
        return self._url
    
    @property
    def m3u8_url(self)->str:
        return self._m3u8_url
    
    @property
    def m3u8_path(self):
        return m3u8_path(self.title)
    @property
    def url_path(self):
        return url_json_path(self.title)
    
    @property
    def temp_dir(self):
        return temp_video_dir(self.title)
    
    @property
    def exist_temp_dir(self)->bool:
        return os.path.exists(self.temp_dir)
    @property
    def exist_m3u8_path(self)->bool:
        return os.path.exists(self.m3u8_path)
    @property
    def suffix(self)->str:
        info=self.info
        if info:
            return info.suffix
        #默认值
        return ".ts"
    
    @property
    def url_data(self):
        data=get_url_data(self.m3u8_url,self.url_path,self.m3u8_path)
        return data
    
    # @property
    # def m3u8_data(self):
    #     url_path=m3u8_path(self.title)
    #     raw_data=read_from_json_utf8_sig(url_path)
    #     if raw_data:
    #         return raw_data
        

    #     if self.has_m3u8_url:
    #         import requests
    #         response=requests.get(url=self.m3u8_url)
    #         raw_data=response.text
    #         write_to_json_utf8_sig(url_path,raw_data)
    #         return raw_data

    #     return raw_data

    
    @property
    def valid(self)->bool:
        return self.has_raw_url or self.has_m3u8_url
    
    @staticmethod
    def from_dict(data:dict)->"VideoUrlInfo":
        return VideoUrlInfo(data.get(video_title_id),data.get(url_id),data.get(m3u8_url_id),data.get(download_status_id),data.get(m3u8_hash_id))
    @property
    def to_dict(self)->dict:
        return {
            video_title_id:self.title,
            url_id:self.url,
            m3u8_url_id:self.m3u8_url,
            download_status_id:self._download,
            m3u8_hash_id:self.m3u8_hash
        }
    def __repr__(self) -> str:
        
        return f"title:{self.title} url:{self.url} m3u8_url:{self.m3u8_url} download:{self._download} m3u8_hash:{self.m3u8_hash}"
