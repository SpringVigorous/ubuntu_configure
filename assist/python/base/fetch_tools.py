from base import exception_decorator,fetch_sync,read_from_bin,write_to_bin,singleton,f_safe_format,file_valid,normal_path,path_equal,logger_helper
import os
from typing import Callable,Any
from pathlib import Path


base_headers={
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36',
}

class TinyFetch():
    def __init__(self,url=None,local_path=None,headers:dict=base_headers,write_func:Callable[[str|Path,Any],Any]=write_to_bin,read_func:Callable[[str|Path],Any]=read_from_bin) -> None:
        self._data=None
        self._headers=base_headers
        self.set_url(url)
        self.set_local_path(local_path)
        self.set_write_func(write_func)
        self.set_read_func(read_func)
        self.set_headers(headers)
        self._url_success:bool=True
        self._logger=logger_helper()
        
    @property
    def logger(self):
        
        self._logger.update_target("获取数据",f"{self.to_dict}")
        
        return self._logger
    def set_url(self,url):
        self._url=url
        
    def set_local_path(self,local_path):
        self._local_path=normal_path(local_path)
        
    def __eq__(self, value: object) -> bool:
        
        # 正确写法：先判断类型
        if value is None:
            return False
        # 1. 先判断 other 是否是当前类的实例（避免类型不匹配报错）
        if not isinstance(value, TinyFetch):
            return False  # 非同类实例直接判定不相等
        # 2. 按业务属性比较（如 name 和 age 都相等，则实例相等）
        
        if self.url_valid and value.url_valid:
            return self.url==value.url
        elif self.local_path_valid and value.local_path_valid:
            return path_equal(self.local_path,value.local_path)
        
        return self.url==value.url and self.local_path==value.local_path
    
        # 重写 __hash__：基于参与 __eq__ 的属性计算哈希值
    def __hash__(self):
        # 用 tuple 包装属性（不可变类型），通过 hash() 计算哈希值
        return hash((self.url, self.local_path))
    
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
        if not self.data_valid: 
            return
        os.makedirs(os.path.dirname(self._local_path), exist_ok=True)
        self._write_func(self._local_path,self._data)
        
    @exception_decorator(error_state=False)
    def _read_from_file(self):
        if not os.path.exists(self._local_path): 
            return None
        return self._read_func(self._local_path)
    
    def _fail_url(self):
        self._url_success=False
    @exception_decorator(error_state=False)
    def _from_url(self):
        #获取过一次，但是没有成功，后续就不要试了
        if not self._url_success:
            self.logger.debug("返回空","原因是上次url获取失败")
            return

        result= fetch_sync(self._url,max_retries=1,timeout=2,headers=self._headers,verify=False)
        if result is None:
            self.logger.error("url获取失败","后续再次通过url获取时，直接返回空")
            
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

        self.set_data(self._read_from_file())
        if self.data_valid: 
            self.logger.trace("local获取成功")
            return self._data

        self.set_data(self._from_url())
        if self.data_valid and  self.local_path_valid and not self.local_valid:
            self._write_to_file()
            self.logger.trace("url获取成功","输出到local")

        return self._data
    
    
    def __repr__(self) -> str:
        result=f_safe_format(self.data)
        max_len=50
        if len(result)>max_len:
            result=f"{result[:max_len]}..."
            
        cur_dict=self.to_dict
        cur_dict["data"]=result
            
        return f"{cur_dict}"
    
    
    @property
    def to_dict(self)->dict:
        return {"url":self.url,"local_path":self.local_path}
    
    @staticmethod
    def from_dict(data:dict)->"TinyFetch":
        return TinyFetch(**data)

@singleton
class TinyCache():
    def __init__(self) -> None:
        self._index_dict={}
        self._cache_data=[] #只增不减
        self.logger=logger_helper("缓存数据")
    def _add_data(self,key,index):
        if not key:
            return
        key=normal_path(key)
        self._index_dict[key]=index
        
        
    def _index(self,fetch_data:TinyFetch)->int:
        if self._exist(fetch_data): 
            return self._cache_data.index(fetch_data)
        return -1
    def _exist(self,fetch_data:TinyFetch)->bool:
        return fetch_data in self._cache_data if self._cache_data else False

    def _add_fetch_data(self,fetch_data:TinyFetch):
        if not isinstance(fetch_data,TinyFetch): 
            return
        
        with self.logger.raii_target(detail=fetch_data) as logger:

            if self. _exist(fetch_data): 
                logger.trace("忽略","数据已存在，无需添加")
            else:
                #先获取下 数据(即生成数据)
                data=fetch_data.data
                if not fetch_data.data_valid: 
                    logger.trace("忽略","数据无效，无需添加")
                    return 
                #添加到缓存中
                self._cache_data.append(fetch_data)
            
            #重新整理索引
            index=self._index(fetch_data)
            if fetch_data.url_valid:
                self._add_data(fetch_data.url,index)
            
            if fetch_data.local_path_valid:
                self._add_data(fetch_data._local_path,index)
                
            logger.trace("成功",f"已添加,索引为:{index}")

    def get_raw_data(self,key)->TinyFetch:
        key=normal_path(key)
        index= self._index_dict.get(key,-1)
        if index >-1:
            return self._cache_data[index]
        return
        
    def get_data(self,key):
        result=self.get_raw_data(key)
        if result:
            return result.data
        return
        
    @exception_decorator(error_state=False)
    def cache(self,url=None,local_path=None,headers:dict=base_headers,write_func:Callable[[str|Path,Any],Any]=write_to_bin,read_func:Callable[[str|Path],Any]=read_from_bin):
        tag={"url":url,"local_path":local_path}
        with self.logger.raii_target(detail=f"{tag}") as logger:
            raw_data=None
            if local_path and (raw_data:=self.get_raw_data(local_path)):
                logger.trace("忽略",f"local_path已存在，无需添加")
                if url:
                    self._add_data(url,index=self._index(raw_data))
                    #填充缺失的 url 字段
                    if not raw_data.url_valid:
                        raw_data.set_url(url)
                return
            
            if url and (raw_data:=self.get_raw_data(url)):
                logger.trace("忽略","url已存在，无需添加")
                if local_path:
                    self._add_data(local_path,index=self._index(raw_data))
                    #填充缺失的 local_path 字段
                    if not raw_data.local_path_valid:
                        raw_data.set_local_path(local_path)
                        
                    # 顺便保存到本地
                    if not file_valid(local_path):
                        try:
                            os.makedirs(os.path.dirname(local_path), exist_ok=True)
                            write_to_bin(local_path,raw_data.data)
                        except Exception as e:
                            logger.error("输出失败",f"{e}")
                return
            
            #说明完全是个新值，按正常流程走
            self._add_fetch_data(TinyFetch(url,local_path,headers,write_func,read_func))
        
        
        
    
    def __repr__(self) -> str:
        import json
        return json.dumps(self._index_dict,indent=4,ensure_ascii=False)

        
        
        
if __name__=="__main__":
    
    
    manager=TinyCache()
    
    manager.cache(url="https://hn.bfvvs.com/play/Rb4QDm2d/index.m3u8",local_path=r"F:\worm_practice\player\temp\宝宝巴士之神奇简笔画_2_35.m3u8")
    manager.cache(url="https://hn.bfvvs.com/play/Yer8NZwb/index.m3u8",local_path=r"F:\worm_practice\player\temp\宝宝巴士之神奇简笔画_2_36.m3u8")
    manager.cache(url="https://hn.bfvvs.com/play/YaOMoYgd/index.m3u8",local_path=r"F:\worm_practice\player\temp\宝宝巴士之神奇简笔画_2_37.m3u8")
    manager.cache(url="https://hn.bfvvs.com/play/yb8172ld/index.m3u8",local_path=r"")
    manager.cache(url="",local_path=r"F:\worm_practice\player\temp\宝宝巴士之神奇简笔画_2_39.m3u8")
    manager.cache(url="https://vv.jisuzyv.com/play/QdJAWNJb/index.m3u8",local_path=r"F:\worm_practice\player\temp\宝宝巴士之神奇简笔画_20.m3u8")


    manager.cache(url="https://hn.bfvvs.com/play/yb8172ld/index.m3u8",local_path=r"F:\worm_practice\player\temp\宝宝巴士之神奇简笔画_2_38.m3u8")
    manager.cache(url="https://hn.bfvvs.com/play/lejZVRze/index.m3u8",local_path=r"F:\worm_practice\player\temp\宝宝巴士之神奇简笔画_2_39.m3u8")
    manager.cache(local_path=r"F:\worm_practice\player\temp\宝宝巴士之神奇简笔画_20.m3u8")
    
    print(manager)