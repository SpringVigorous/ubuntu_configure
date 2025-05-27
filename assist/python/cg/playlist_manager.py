import sys
from queue import Queue
import threading

from pathlib import Path
import os
import pandas as pd
root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )
from base import (
    logger_helper,UpdateTimeType,exception_decorator,except_stack,df_empty,sequence_num_file_path,
    
    xml_tools,
    concat_dfs,
    unique_df,
    merge_df,
    update_col_nums,
    assign_col_numbers,
    mp4_files,

    concat_unique,
    content_same,
    sub_df,
    set_attr,
    get_attr,
    file_manager,
    read_from_json_utf8_sig,
    
)
from typing import Callable



from playlist_config import *

class playlist_manager(file_manager):
    _instance = None
    _lock = threading.Lock()    
    _initialized = False  # 初始化标志位

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    # 创建实例但不调用 __init__
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, *args, **kwargs):
        # 确保初始化仅执行一次
        if  self.__class__._initialized:
            return
        
        with self.__class__._lock:
            if  self.__class__._initialized:
                return
            # 实际初始化逻辑
            super().__init__()
            # 初始化标志位
            self.__class__._initialized = True
            #更新状态
            self.update_status()
            
    @property
    def video_df(self):
        return self._set_df_name(self._video_df,video_sheet_name) 
    
    
    
    
    
    @exception_decorator(error_state=False)
    def read_xlsx_df(self):
        logger=self.logger
        logger.update_target("读取数据",video_xlsx)
        logger.update_time(UpdateTimeType.STAGE)
        dfs=self._read_xlsx_df_imp(video_xlsx,sheet_names=[video_sheet_name])
        if not dfs:
            return
        with self.lock:
            self._video_df=dfs[0]
        logger.debug("完成",update_time_type=UpdateTimeType.STAGE)
        
    @exception_decorator(error_state=False)
    def save_xlsx_df(self):
        logger=self.logger
        logger.update_time(UpdateTimeType.STAGE)
        logger.trace("开始")
        
        def _save_imp(xlsx_path:str):
            logger.update_target("保存数据",xlsx_path)
            self._save_df_xlsx_imp([self.video_df],xlsx_path)
        try:
            _save_imp(video_xlsx)
        except:
            xlsx_path=sequence_num_file_path(video_xlsx)
            logger.error("失败",f"备份到{xlsx_path},具体错误信息入下：\n{except_stack()}\n", update_time_type=UpdateTimeType.STAGE)
            logger.update_time(UpdateTimeType.STAGE)
            _save_imp(xlsx_path)

        logger.trace("完成",update_time_type=UpdateTimeType.STAGE)
        
    @exception_decorator(error_state=False)
    def update_video_df(self,new_df:pd.DataFrame)->pd.DataFrame:
        with self.lock:
            keys=[m3u8_url_id]
            arrage_func:Callable[[pd.DataFrame],pd.DataFrame]=None
            new_data_func:Callable[[pd.Series],None]=None
            self._video_df,new_df= self._update_df(self.video_df,new_df,keys,arrage_func,new_data_func)
            return new_df
        
    
        
    @property
    def urls(self):
        if  df_empty(self._video_df):
            return []
        return self._video_df[url_id].tolist()
        
    @property
    def m3u8_urls(self):
        if  df_empty(self._video_df):
            return []
        return self._video_df[m3u8_url_id].tolist()
        
    @property
    @exception_decorator(error_state=False)
    def undownloaded_lst(self)->list:
        if  df_empty(self._video_df):
            return []
        
        results=[]
        for _,row in self._video_df[self._video_df[download_status_id]<1].iterrows():
            video_name=row[video_name_id]
            url_path=url_json_path(video_name)
            data=read_from_json_utf8_sig(url_path)
            if not data:
                continue
            from base import base64_utf8_to_bytes
            key,iv,info_list,total_len,m3u8_url=data["key"],data["iv"],data["playlist"],data["total_len"],data["url"]
            if key:
                key=base64_utf8_to_bytes(key)
            if iv:
                iv=base64_utf8_to_bytes(iv)
            results.append((key,iv,info_list,total_len,video_name,m3u8_url))
            
        return results

    @exception_decorator(error_state=False)
    def has_downloaded(self,video_name:str)->bool:
        df=None
        with self.lock:
            df=self._video_df.copy()
        
        if df_empty(df):
            return False
        
        from base.df_tools import  find_last_value_by_col_val
        
        return find_last_value_by_col_val(df,video_name_id,video_name,download_status_id)>0
    
    
    @exception_decorator(error_state=False)
    def set_donwnloaded(self,video_name:str,status:int=1)->bool:
        logger=self.logger
        logger.update_target("设置文件下载状态",video_name)
        with self.lock:
            df=self._video_df
            if df_empty(df):
                return False
            mask=df[video_name_id]==video_name
            if not mask.any():
                return False
            df.loc[mask, download_status_id] = status
            logger.debug("已下载" if status>0 else "未下载",update_time_type=UpdateTimeType.STAGE)
            return True
    @exception_decorator(error_state=False)
    def update_status(self):
        for file in mp4_files(video_dir):
            cur_path=Path(file)
            self.set_donwnloaded(cur_path.stem,1)