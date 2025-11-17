
from base import xlsx_manager,singleton,df_empty,exception_decorator,TaskStatus,find_rows_by_col_val,global_logger,audio_root,find_last_value_by_col_val,is_df
from pathlib import Path
import json
import pandas as pd
from audio_kenel import *
import os
from enum import IntFlag

class SheetType(IntFlag):
    ALBUM=0
    AUDIO=1
    CATALOG=2
    
    @property
    def is_album(self)->bool:
        return self==SheetType.ALBUM
    
    @property
    def is_audio(self)->bool:
        return self==SheetType.AUDIO
    
    @property
    def is_catalog(self)->bool:
        return self==SheetType.CATALOG

audio_xlsx_root=audio_root/"xlsx"
audio_html_root=audio_root/"html"
audio_media_root=audio_root/"media"





@singleton
class AudioManager(xlsx_manager):
    def __init__(self) -> None:
        super().__init__()
        self.logger.update_target(detail="音频文件管理")
        self._df_flags={}
        self._init_catalog()
        self._ignore_sound=False
        self._ignore_album=False
        

    def set_ignore_album(self,ignore:bool):
        self._ignore_album=ignore
    @property
    def ignore_album(self):
        return self._ignore_album

    def set_ignore_sound(self,ignore:bool):
        self._ignore_sound=ignore
        
    def filter_can_download_df(self,df:pd.DataFrame)->pd.DataFrame:
        if df_empty(df):
            return df
        
        mask=df[downloaded_id].apply(lambda x: TaskStatus.from_value(x).can_download)
        #条件筛选
        return df[mask]

    def rest_temp_cancel_df(self,df:pd.DataFrame)->pd.DataFrame:
        if df_empty(df):
            return df
        
        for index,row in df.iterrows():
            df.iloc[index,downloaded_id]=TaskStatus.from_value(row[downloaded_id]).clear_temp_canceled.value

        #条件筛选
        return df
    def set_temp_cancel_df(self,df:pd.DataFrame)->pd.DataFrame:
        if df_empty(df):
            return df
        
        for index,row in df.iterrows():
            df.iloc[index,downloaded_id]=TaskStatus.from_value(row[downloaded_id]).set_temp_canceled.value

        #条件筛选
        return df
    @property
    def force_ignore_sound(self):
        return self._ignore_sound  
        
    @staticmethod
    def xlsx_root()->Path:
        return audio_root/"xlsx"
        
    @staticmethod
    def html_root()->Path:
        return audio_root/"html"
    
    @staticmethod
    def media_root()->Path:
        return audio_root/"audio"
    
    #目录文件路径
    @staticmethod
    def catalog_xlsx_info()->tuple[Path,str]:
        return AudioManager.xlsx_root()/"catalog.xlsx","catalog"
    
    
    @staticmethod
    def author_xlsx_info(author_name:str)->tuple[str|Path,str]:
        return AudioManager.xlsx_root()/f"{author_name}.xlsx",album_sheet_name
        # return AudioManager.xlsx_root()/title/"title.xlsx",album_sheet_name
    
    
    
    @staticmethod
    def album_xlsx_info(author_name:str,album_name:str)->tuple[str|Path,str]:
        return AudioManager.xlsx_root()/author_name/f"{album_name}_album.xlsx",audio_sheet_name
    
    
    @staticmethod
    def author_html_path(title:str)->Path:
        return AudioManager.html_root()/f"{title}.html"
        
    
    
    @staticmethod
    def album_path(file_name:str)->Path:
        name=Path(file_name).stem
        return AudioManager.file_path(file_name,name,name)
    
    @staticmethod
    def file_path(file_name:str,author_name=None,album_name=None):
        suffix_dict={
            ".xlsx":AudioManager.xlsx_root(),
            ".html":AudioManager.html_root(),
            ".m4a":AudioManager.media_root(),
            ".mp3":AudioManager.media_root(),
            ".mp4":AudioManager.media_root(),
        }      
        suffix= Path(file_name).suffix
        root=suffix_dict.get(suffix,AudioManager.media_root())
        def _get_dir(rel_name):
            return root/rel_name if rel_name else root
        root= _get_dir(author_name)
        root= _get_dir(album_name)
        
        
        return root/file_name

    @staticmethod
    def current_dir(dir_name,referent_file_path):
        pass

    def _init_catalog(self):
        if SheetType.CATALOG not in self._df_flags.values():
            xlsx_path,sheet_name=AudioManager.catalog_xlsx_info()
            df=self.get_df(xlsx_path,sheet_name)
            if not is_df(df): 
        
                df=pd.DataFrame(columns=[     
                        href_id,
                        author_id,
                        downloaded_id,
                        local_path_id,
                        album_count_id,
                        downloaded_count_id,
                        ])
                

            self.cache_catalog_df(xlsx_path,sheet_name,df)

    @exception_decorator(error_state=False,error_return=None)
    def _filter_dfs(self,df_type:SheetType)->list[tuple[str,str,pd.DataFrame]]:
        results=[]
        
        for (xlsx_path,sheet_name),audio_ in self._df_flags.items():
            if df_type !=audio_:
                continue
            df=self.get_df(xlsx_path,sheet_name)
            if  not df is None and isinstance(df,pd.DataFrame): 
                results.append((xlsx_path,sheet_name,df))
        return results
    
    @property
    def audio_dfs(self)->list[tuple[str,str,pd.DataFrame]]:
        return self._filter_dfs(df_type=SheetType.AUDIO)
    
    @property
    def album_dfs(self)->list[tuple[str,str,pd.DataFrame]]:
        return self._filter_dfs(df_type=SheetType.ALBUM)
    
    @property
    def catalog_df(self)->tuple[str,str,pd.DataFrame]:
        if results:=self._filter_dfs(df_type=SheetType.CATALOG):
            return results[0]
        return (None,None,None)
    
    def cache_audio_df(self,xlsx_path,sheet_name,df:pd.DataFrame):
        AudioManager.init_df_status(df)
        df=AudioManager.update_df_status(df)
        self.cache_df(xlsx_path,sheet_name,df)
        self._df_flags[(xlsx_path,sheet_name)]=SheetType.AUDIO
        
    def cache_albumn_df(self,xlsx_path,sheet_name,df:pd.DataFrame):
        AudioManager.init_df_status(df)
        df=self.update_summary_df(df)
        self.cache_df(xlsx_path,sheet_name,df)
        self._df_flags[(xlsx_path,sheet_name)]=SheetType.ALBUM
    
    def cache_catalog_df(self,xlsx_path,sheet_name,df:pd.DataFrame):
        # AudioManager.init_df_status(df)

        self.cache_df(xlsx_path,sheet_name,df)
        self._df_flags[(xlsx_path,sheet_name)]=SheetType.CATALOG
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
        
        if media_url_id not in df.columns:
            df[media_url_id] = ""
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
                global_logger().error("任务状态错误", "|".join(map(str, row.index)))
                return row[downloaded_id]
        # 仅对掩码为 True 的行应用赋值（axis=1 表示按行处理）
        df.loc[mask, downloaded_id] = df.loc[mask].apply( update_flag,
            axis=1
        )

        return df
    #更新专辑状态及已下载数
    @exception_decorator(error_state=False)
    def update_summary_df(self,df:pd.DataFrame)->pd.DataFrame:
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
            
            #添加忽略状态
            if not new_status.is_success and self.ignore_album:
                new_status!= TaskStatus.TEMP_CANCELED
                
            
            
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
                result_df=find_rows_by_col_val(df,href_id,href_val)
                if df_empty(result_df): 
                    logger.debug("忽略更新","查找的href不存在")
                    return
                for index,row in result_df:
                    df.iloc[index,downloaded_id]=status.value
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
    def update_status_suffix_url(self,xlsx_path,sheet_name,href_val:str,status:TaskStatus,suffix:str,media_url:str):
        logger_info={
            "xlsx_path":xlsx_path,
            "sheet_name":sheet_name,
            "url":href_val,
            "status":status,
            "suffix":suffix,
            "media_url":media_url
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
                    if media_url:
                        df.loc[index,media_url_id]=media_url
                            
                logger.trace("成功")
            except Exception as e:
                logger.error("更新失败",e)
            
    #更新博主专辑数
    @exception_decorator(error_state=False)
    def update_author_album_count(self,href_val:str,count:int):
        df=self.catalog_df
        if df_empty(df):
            self.logger.debug("忽略更新","df不存在")
            return
        logger_info={
            href_id:href_val,
            album_count_id:count,
        }
        with self.logger.raii_target("更新博主专辑数",f"{logger_info}") as logger:
            try:
                for index,row in find_rows_by_col_val(df,href_id,href_val).iterrows():
                        df.loc[index,album_count_id]=count
                logger.trace("成功")
            except Exception as e:
                logger.error("更新失败",e)
            pass
        
    
    @exception_decorator(error_state=False)
    def author_name_from_catalog(self,url)->str:
        if result:=self.author_info(url):
            return result.get(author_id)

    
    
    @exception_decorator(error_state=False)
    def author_info(self,url)->dict:
        xlsx_path,sheet_name,catalog_df= self.catalog_df
        if df_empty(catalog_df): 
            return 
        df= find_rows_by_col_val(catalog_df,href_id,url)
        if df_empty(df): 
            return
        
        return df.iloc[0].to_dict()
    @exception_decorator(error_state=False)
    def before_save(self)->bool:
        def _update_df_status(xlsx_path,sheet_name,df):
            if df_empty(df): return
            df=self.update_summary_df(df)
            self.cache_df(xlsx_path,sheet_name,df)
        
        #保存前，更新专辑信息
        if album_dfs:=self.album_dfs:
            for xlsx_path,sheet_name,df in album_dfs:
                _update_df_status(xlsx_path,sheet_name,df)
        if catalog_result:=self.catalog_df:
            xlsx_path,sheet_name,df=catalog_result
            _update_df_status(xlsx_path,sheet_name,df)