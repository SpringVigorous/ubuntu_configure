
from base import xlsx_manager,singleton,df_empty,exception_decorator,TaskStatus,find_rows_by_col_val,global_logger
from pathlib import Path
import json
import pandas as pd
from audio_kenel import *
import os
@singleton
class AudioManager(xlsx_manager):
    def __init__(self) -> None:
        super().__init__()
        self.logger.update_target(detail="音频文件管理")
        self._df_flags={}
        
    def _filter_dfs(self,is_audio=True)->list[tuple]:
        results=[]
        
        for (xlsx_path,sheet_name),audio_ in self._df_flags.items():
            if is_audio !=audio_:
                continue
            df=self.get_df(xlsx_path,sheet_name)
            if not df_empty(df): 
                results.append((xlsx_path,sheet_name,df))
        return results
    
    @property
    def audio_dfs(self):
        return self._filter_dfs(is_audio=True)
    
    @property
    def album_dfs(self):
        return self._filter_dfs(is_audio=False)
    
    
    def cache_audio_df(self,xlsx_path,sheet_name,df:pd.DataFrame):
        AudioManager.init_df_status(df)
        df=AudioManager.update_df_status(df)
        self.cache_df(xlsx_path,sheet_name,df)
        self._df_flags[(xlsx_path,sheet_name)]=True
        
    def cache_albumn_df(self,xlsx_path,sheet_name,df:pd.DataFrame):
        AudioManager.init_df_status(df)
        df=self.update_album_df(df)
        self.cache_df(xlsx_path,sheet_name,df)
        self._df_flags[(xlsx_path,sheet_name)]=False
    
    #初始化
    @staticmethod
    def init_df_status(df):
        if df_empty(df): 
            return df
        # 2. 修正列名拼写错误，判断是否存在目标列
        if downloaded_id not in df.columns:
            # 可选：如果列不存在，可初始化（根据你的需求决定是否添加）
            df[downloaded_id] = TaskStatus.UNDOWNLOADED.value  # 初始化所有值为TaskStatus.UNDOWNLOADED（后续会被更新）
        # 3. 核心逻辑：仅给 downloaded < 0 的行重新赋值，>=0 的行不变
        # 构建条件掩码（定位需要更新的行）
        
        #判断是否是旧状态，是的话，就改成新的
        unique_vals = set(df[downloaded_id].unique())
        if unique_vals.issubset({1, -1}):
            undownload_mask=df[downloaded_id] ==-1
            df.loc[undownload_mask, downloaded_id] = [TaskStatus.UNDOWNLOADED.value]*undownload_mask.sum()
            
            download_mask=df[downloaded_id] ==1
            df.loc[download_mask, downloaded_id] = [TaskStatus.SUCCESS.value]*download_mask.sum()
        else:
            #转换为 枚举类
            # df[downloaded_id]=df[downloaded_id].append(TaskStatus.from_value)
            pass
        
    #根据是否存在，更新状态
    @staticmethod
    def update_df_status(df):
        mask = df[downloaded_id] !=TaskStatus.SUCCESS.value
        if not mask.any():
            return df
        def update_flag(row):
            try:
                return TaskStatus.SUCCESS.value if  os.path.exists(row[local_path_id]) else row[downloaded_id]
            except:
                global_logger().error("标志位错误", "|".join(map(str, row.index)))
                return row[downloaded_id]
        # 仅对掩码为 True 的行应用赋值（axis=1 表示按行处理）
        df.loc[mask, downloaded_id] = df.loc[mask].apply( update_flag,
            axis=1
        )

        return df
    #更新专辑状态及已下载数
    @exception_decorator(error_state=False)
    def update_album_df(self,df:pd.DataFrame)->pd.DataFrame:
        if not isinstance(df,pd.DataFrame):
            return 
        
        
        if local_path_id not in df.columns:
            return df
        for index,row in df.iterrows():
            if row[downloaded_id]==TaskStatus.SUCCESS.value: #已下载
                continue
            
            xlsx_path=row[local_path_id]
            dest_df= self.get_df(xlsx_path,sheet_name=audio_sheet_name)
            if  df_empty(dest_df): 
                continue
            #已下载数
            
            dest_col_mask=dest_df[downloaded_id]==TaskStatus.SUCCESS.value
            df.loc[index,downloaded_count_id] =dest_col_mask.sum()
            
            # 修改后：清晰的条件判断逻辑
            if dest_col_mask.all():
                new_status = TaskStatus.SUCCESS
            elif dest_col_mask.any():
                new_status = TaskStatus.INCOMPLETED
            else:
                new_status = TaskStatus.UNDOWNLOADED
            
            df.loc[index,downloaded_id]=new_status.value
        
        return df


    #更新下载状态
    @exception_decorator(error_state=False)
    def update_status(self,xlsx_path,sheet_name,href_val:str,status:TaskStatus):
        with self.logger.raii_target("更新下载下载状态",f"{xlsx_path}:{sheet_name}:{href_val}:{status}") as logger:
            df=self.get_df(xlsx_path,sheet_name)
            if df_empty(df):
                logger.debug("忽略更新","df不存在")
                return
            try:
                for index,row in find_rows_by_col_val(df,href_id,href_val).items():
                    df.loc[index,downloaded_id]=status.value
                    logger.trace("成功")
            except Exception as e:
                logger.error("更新失败",e)
    #更新本地文件后缀名
    @exception_decorator(error_state=False)
    def update_suffix(self,xlsx_path,sheet_name,href_val:str,suffix:str):
        if not suffix or suffix==base_suffix:
            return
        with self.logger.raii_target("更新下载文件后缀",f"{xlsx_path}:{sheet_name}:{href_val}:{suffix}") as logger:

            df=self.get_df(xlsx_path,sheet_name)
            if df_empty(df):
                logger.debug("忽略更新","df不存在")
                return
            try:
            
                for index,row in find_rows_by_col_val(df,href_id,href_val).items():
                    df.loc[index,local_path_id]=str(Path(row[local_path_id]).with_suffix(suffix))
                logger.trace("成功")
            except Exception as e:
                logger.error("更新失败",e)
    #更新下载状态
    @exception_decorator(error_state=False)
    def update_status_suffix(self,xlsx_path,sheet_name,href_val:str,status:TaskStatus,suffix:str):
        logger_info={
            "xlsx_path":xlsx_path,
            "sheet_name":sheet_name,
            "url":href_val,
            "status":status,
            "suffix":suffix
        }
        
        with self.logger.raii_target("更新下载状态及文件后缀",f"{logger_info}") as logger:
            df=self.get_df(xlsx_path,sheet_name)
            if df_empty(df):
                logger.debug("忽略更新","df不存在")
                return
            try:
                for index,row in find_rows_by_col_val(df,href_id,href_val).iterrows():
                    if status is not None:
                        df.loc[index,downloaded_id]=status.value #转换为整型
                    if suffix:
                        if cur_path:=row[local_path_id]:
                            df.loc[index,local_path_id]=str(Path(cur_path).with_suffix(suffix))
                logger.trace("成功")
            except Exception as e:
                logger.error("更新失败",e)
            
    
            