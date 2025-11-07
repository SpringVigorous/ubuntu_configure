from base import exception_decorator,fetch_sync,read_from_bin,write_to_bin,singleton,f_safe_format,file_valid,normal_path,path_equal
import os
from typing import Callable,Any
from pathlib import Path


base_headers={
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36',
}

class FetchData():
    def __init__(self,url=None,local_path=None,headers:dict=base_headers,write_func:Callable[[str|Path,Any],Any]=write_to_bin,read_func:Callable[[str|Path],Any]=read_from_bin) -> None:
        self._data=None
        self._headers=base_headers
        self.set_url(url)
        self.set_local_path(local_path)
        self.set_write_func(write_func)
        self.set_read_func(read_func)
        self.set_headers(headers)
        self._url_success:bool=True
        
    def set_url(self,url):
        self._url=url
        
    def set_local_path(self,local_path):
        self._local_path=normal_path(local_path)
        
    @property
    def url(self)->str:
        return self._url
    
    @property
    def local_path(self)->str:
        return self._local_path
        
    def set_headers(self,headers:dict):
        if not isinstance(headers,dict) or not headers:
            return
            
        self._headers=headers
        self._headers.update(base_headers)
    
    def set_data(self,data):
        self._data=data
        
    def set_write_func(self,write_func:Callable[[str|Path,Any],Any]):
        self._write_func=write_func
        
    def set_read_func(self,read_func:Callable[[str|Path],Any]):
        self._read_func=read_func    
        
    @exception_decorator(error_state=False)
    def _write_to_file(self):
        if not self.data_valid and os.path.exists(self._local_path): 
            return
        os.makedirs(os.path.dirname(self._local_path), exist_ok=True)
        self._write_func(self._local_path,self._data)
        
    @exception_decorator(error_state=False)
    def _read_from_file(self):
        if not os.path.exists(self._local_path): 
            return None
        return self._read_func(self._local_path)
    
    @exception_decorator(error_state=False)
    def _from_url(self):
        #获取过一次，但是没有成功，后续就不要试了
        if not self._url_success:
            return

        result= fetch_sync(self._url,max_retries=1,timeout=2,headers=self._headers,verify=False)
        if result is None:
            self._url_success=False
        return result
        
    @property
    def data_valid(self)->bool:
        return isinstance(self._data,bool) or  bool(self._data)
    
    @property
    def url_valid(self)->bool:
        return bool(self._url)
    
    @property
    def local_path_valid(self)->bool:
        return bool(self.local_path)
    @property
    def local_valid(self)->bool:
        return file_valid(self.local_path)
    
    @property
    def data(self):
        if self.data_valid:
            return self._data

        self.set_data(self._read_from_file() or self._from_url())
        if self.data_valid and  self.local_path_valid and not self.local_valid:
            self._write_to_file()

        return self._data
    
    
    def __repr__(self) -> str:
        result=f_safe_format(self.data)
        return f"url:{self.url},local_path:{self.local_path},data:{result}"

@singleton
class CacheFetchData():
    def __init__(self) -> None:
        self._data={}
        self._cache_data=[]
    def _add_data(self,key,index):
        
        key=normal_path(key)
        
        self._data[key]=index
        
        
    def _index(self,fetch_data:FetchData)->int:
        if self._exist(fetch_data): 
            return self._cache_data.index(fetch_data)
        return -1
    def _exist(self,fetch_data:FetchData)->bool:
        return fetch_data in self._cache_data if self._cache_data else False

    def _add_fetch_data(self,fetch_data:FetchData):
        if not isinstance(fetch_data,FetchData): 
            return
        #先获取下 数据，避免
        data=fetch_data.data
        if not fetch_data.data_valid: 
            return 
        if self. _exist(fetch_data): 
            return
        
        self._cache_data.append(fetch_data)
        index=self._index(fetch_data)

        if fetch_data.url_valid:
            self._add_data(fetch_data.url,index)
        
        if fetch_data.local_path_valid:
            self._add_data(fetch_data._local_path,index)

    def get_raw_data(self,key)->FetchData:
        key=normal_path(key)
        index= self._data.get(key)
        if index >-1:
            return self._cache_data[index]
        return
        
    def get_data(self,key):
        result=self.get_raw_data(key)
        if result:
            return result.data
        return
        
    def cache_data(self,url=None,local_path=None,headers:dict=base_headers,write_func:Callable[[str|Path,Any],Any]=write_to_bin,read_func:Callable[[str|Path],Any]=read_from_bin):
        self._add_fetch_data(FetchData(url,local_path,headers,write_func,read_func))
        
        
        
    
    def __repr__(self) -> str:
        return "\n".join([f_safe_format(x) for x in self._data.values()])
        
        
        
if __name__=="__main__":
    
    
    manager=CacheFetchData()
    
    manager.cache_data(url="https://yzzy.play-cdn10.com/20230107/21727_ffde5c2c/1000k/hls/mixed.m3u8",local_path=r"F:\worm_practice\player\temp\汪汪队立大功_第02季_21.m3u8")
    manager.cache_data(url="https://yzzy.play-cdn10.com/20230107/21728_69d592f1/1000k/hls/mixed.m3u8",local_path=r"F:\worm_practice\player\temp\汪汪队立大功_第02季_22.m3u8")
    manager.cache_data(url="https://yzzy.play-cdn10.com/20230107/21729_a1a116b2/1000k/hls/mixed.m3u8",local_path=r"F:\worm_practice\player\temp\汪汪队立大功_第02季_23.m3u8")
    manager.cache_data(url="https://yzzy.play-cdn10.com/20230107/21730_08313c1a/1000k/hls/mixed.m3u8",local_path=r"F:\worm_practice\player\temp\汪汪队立大功_第02季_24.m3u8")
    manager.cache_data(url="https://yzzy.play-cdn10.com/20230107/21732_acfefaa9/1000k/hls/mixed.m3u8",local_path=r"F:\worm_practice\player\temp\汪汪队立大功_第02季_25.m3u8")
    manager.cache_data(url="https://yzzy.play-cdn10.com/20230107/21731_fa138127/1000k/hls/mixed.m3u8",local_path=r"F:\worm_practice\player\temp\汪汪队立大功_第02季_26.m3u8")


    
    print(manager)