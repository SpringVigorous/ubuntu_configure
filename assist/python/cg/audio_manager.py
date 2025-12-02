
from pathlib import Path
import json
import os

from base import (
    # 核心工具
    singleton,
    exception_decorator,
    global_logger,
    path_equal,
    
    # 数据处理模块
    xlsx_manager,
    df_empty,
    is_df,
    concat_dfs,
    find_rows_by_col_val,
    find_last_value_by_col_val,
    arabic_numbers,
    # 业务枚举
    TaskStatus,
    UpdateTimeType,
    
    # 路径配置
    audio_root,
    normal_path
)
import pandas as pd
from audio_kenel import *
import os
from enum import IntFlag
from audio_message import AlbumUpdateMsg
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
        self._ignore_sound=False
        self._ignore_album=False

        self.load()

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
        
        mask=df.apply(lambda row: TaskStatus.from_value(row[downloaded_id]).can_download or os.path.exists(row[local_path_id]),axis=1)
        
        # mask=df[downloaded_id].apply(lambda x: TaskStatus.from_value(x).can_download)
        #条件筛选
        return df[mask]

    def rest_temp_cancel_df(self,df:pd.DataFrame)->pd.DataFrame:
        if df_empty(df):
            return df
        
        for index,row in df.iterrows():
            df.loc[index,downloaded_id]=TaskStatus.from_value(row[downloaded_id]).clear_temp_canceled.value

        #条件筛选
        return df
    def set_temp_cancel_df(self,df:pd.DataFrame)->pd.DataFrame:
        if df_empty(df):
            return df
        
        for index,row in df.iterrows():
            df.loc[index,downloaded_id]=TaskStatus.from_value(row[downloaded_id]).set_temp_canceled.value

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
    def media_suffix()->list[str]:
        return [".m4a",".mp4",".mp3",".acc"]
    
    @staticmethod
    def album_path(file_name:str)->Path:
        name=Path(file_name).stem
        return AudioManager.file_path(file_name,name,name)
    
    @staticmethod
    def file_path(file_name:str,author_name=None,album_name=None):
        suffix_dict={
            ".xlsx":AudioManager.xlsx_root(),
            ".html":AudioManager.html_root(),
        }
        
        for media in AudioManager.media_suffix():
            suffix_dict[media]=AudioManager.media_root()
        
              
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
            
            with self.logger.raii_target(detail=xlsx_path) as logger:
            
                df=self.get_df(xlsx_path,sheet_name)
                has_df=is_df(df)
                if not has_df: 
                    df=pd.DataFrame(columns=[     
                            href_id,
                            author_id,
                            downloaded_id,
                            local_path_id,
                            album_count_id,
                            downloaded_count_id,
                            status_id,
                            ])
                    

                self.cache_catalog_df(xlsx_path,sheet_name,df)
                logger.info("完成","从文件读取" if has_df else "直接初始化",update_time_type=UpdateTimeType.STAGE)
    @exception_decorator(error_state=False,error_return=None)
    def load(self):
        self.logger.update_time(UpdateTimeType.ALL)
        with self.logger.raii_target("读取xlsx") as catalog_logger:
            #初始化
            self._init_catalog()
            #catalog
            xlsx_path,name,catalog_df=self.catalog_df
            if df_empty(catalog_df) :
                return
            #author
            for _,catalog_row in catalog_df.iterrows():
                author_path= catalog_row[local_path_id]
                with self.logger.raii_target(detail=author_path) as author_logger:
                    author_df=self.get_df(author_path,album_id)
                    if df_empty(author_df) :
                        author_logger.debug("不存在",update_time_type=UpdateTimeType.STAGE)
                        continue
                    self.cache_author_df(author_path,album_id,author_df)

                    #album
                    for _,author_row in author_df.iterrows():
                        album_path= author_row[local_path_id]               
                        with self.logger.raii_target(detail=album_path) as album_logger:
                            album_df=self.get_df(album_path,audio_sheet_name)
                            if df_empty(album_df):
                                album_logger.debug("不存在",update_time_type=UpdateTimeType.STEP)
                                continue

                            self.cache_album_df(album_path,audio_sheet_name,album_df)
                            album_logger.info("成功",update_time_type=UpdateTimeType.STEP)
                
                    author_logger.info("成功",update_time_type=UpdateTimeType.STAGE)
        catalog_logger.info("成功",f"共{len(self._df_dict)}个表",update_time_type=UpdateTimeType.ALL)
    @exception_decorator(error_state=False,error_return=None)
    def _filter_dfs(self,df_type:SheetType)->list[tuple[str,str,pd.DataFrame]]:
        results=[]
        
        for (xlsx_path,sheet_name),audio_ in list(self._df_flags.items()):
            if df_type !=audio_:
                continue
            df=self.get_df(xlsx_path,sheet_name)
            if  not df is None and isinstance(df,pd.DataFrame): 
                results.append((xlsx_path,sheet_name,df))
        return results
    
    
    
    
    
    @property
    def album_dfs(self)->list[tuple[str,str,pd.DataFrame]]:
        return self._filter_dfs(df_type=SheetType.AUDIO)
    
    @property
    def author_dfs(self)->list[tuple[str,str,pd.DataFrame]]:
        return self._filter_dfs(df_type=SheetType.ALBUM)
    
    @property
    def catalog_df(self)->tuple[str,str,pd.DataFrame]:
        if results:=self._filter_dfs(df_type=SheetType.CATALOG):
            return results[0]
        return (None,None,None)
    
    def cache_album_df(self,xlsx_path,sheet_name,df:pd.DataFrame):
        AudioManager.init_df_status(df)
        df=AudioManager.update_df_status(df)
        column_names= df.columns
        if view_count_id not in column_names:
            df[view_count_id]=-1
        if duration_id not in column_names:
            df[duration_id]=-1

        self.cache_df(xlsx_path,sheet_name,df)
        self._df_flags[(xlsx_path,sheet_name)]=SheetType.AUDIO
        
    def cache_author_df(self,xlsx_path,sheet_name,df:pd.DataFrame):
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
        if df_empty(df):
            return
        
        
        
        # mask = df[downloaded_id] !=TaskStatus.TaskStatus.SUCCESS.value
        mask = df[downloaded_id].apply(lambda x: not TaskStatus.from_value(x).has_reason)
        if not mask.any():
            return df
        def update_flag(row):
            try:
                cur_path=row[local_path_id]
                return TaskStatus.SUCCESS.value if isinstance(cur_path,str) and os.path.exists(cur_path) else row[downloaded_id]
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
                for index,row in result_df.iterrows():
                    df.loc[index,downloaded_id]=status.value
                logger.info("成功")
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
            
                for index,row in find_rows_by_col_val(df,href_id,href_val).iterrows():
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
    #更新下载状态
    @exception_decorator(error_state=False)
    def update_album_df(self,info:AlbumUpdateMsg):
        if not info or not isinstance(info,AlbumUpdateMsg) or not info.valid: 
            return
        status=info.status
        suffix=info.suffix

        
        with self.logger.raii_target("更新下载状态及文件后缀",f"{info}") as logger:
            df=self.get_df(info.xlsx_path,info.sheet_name)
            if df_empty(df):
                logger.debug("忽略更新","df不存在")
                return
            try:
                for index,row in find_rows_by_col_val(df,href_id,info.sound_url).iterrows():
                    if status is not None:
                        df.loc[index,downloaded_id]=status.value #转换为整型
                    if suffix:
                        if cur_path:=row[local_path_id]:
                            df.loc[index,local_path_id]=str(Path(cur_path).with_suffix(suffix))
                    if info.media_url_valid:
                        df.loc[index,media_url_id]=info.media_url
                    if info.duration_valid:
                        df.loc[index,duration_id]=info.duration
                    if info.relase_time_valid:
                        df.loc[index,release_time_id]=info.release_time
                    if info.view_count_valid:
                        df.loc[index,view_count_id]=arabic_numbers(info.view_count)
                            
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
    def export_summary_df(self)->pd.DataFrame:
        audio_summary_xlsx_path=audio_xlsx_root/"summary"/"summary.xlsx"

        
        summary_df=None
        with self.logger.raii_target(detail=f"输出汇总表：{audio_summary_xlsx_path}") as logger:
            self.logger.update_time(UpdateTimeType.STEP)
            #归纳xlsx
            album_dfs=self.album_dfs
            if not album_dfs:
                return
            lst_dfs=[]
            for xlsx_path,sheet_name,summary_df in album_dfs:
                temp=summary_df.copy()
                temp[album_path_id]=xlsx_path
                lst_dfs.append(temp)
                
            summary_df=concat_dfs(lst_dfs)
            if df_empty(summary_df):
                return
            
            os.makedirs(audio_summary_xlsx_path.parent,exist_ok=True)
            summary_df.to_excel(audio_summary_xlsx_path,sheet_name="audio",index=False)
            logger.info("成功",f"共{summary_df.shape[0]}条",update_time_type=UpdateTimeType.STEP)
        return summary_df
        
    
    
    @staticmethod
    def clear_df_temp_canceled(df:pd.DataFrame)->pd.DataFrame:
        if df_empty(df):
            return 
        
        
        for index,row in df.iterrows():
            df.loc[index,downloaded_id]=TaskStatus.from_value(row[downloaded_id]).clear_temp_canceled.value
            
        return df
    
    @exception_decorator(error_state=False)
    def clear_temp_canceled(self,xlsx_path,sheet_name):  
        df=self.get_df(xlsx_path,sheet_name)
        if df_empty(df):
            return 
        AudioManager.clear_df_temp_canceled(df)

        
    @exception_decorator(error_state=False)
    def before_save(self)->bool:
        def _update_df_status(xlsx_path,sheet_name,df):
            if df_empty(df): return
            df:pd.DataFrame=self.update_summary_df(df)
            df.drop_duplicates(subset=[href_id],inplace=True)
            
            self.cache_df(xlsx_path,sheet_name,df)
        
        #保存前，更新专辑信息
        if album_dfs:=self.author_dfs:
            for album_xlsx_path,sheet_name,df in album_dfs:
                _update_df_status(album_xlsx_path,sheet_name,df)
        if catalog_result:=self.catalog_df:
            album_xlsx_path,sheet_name,df=catalog_result
            _update_df_status(album_xlsx_path,sheet_name,df)
            
            
        #更新状态名称
        for album_xlsx_path,sheet_name,df in self.df_lst:
            df[status_id]= df[downloaded_id].apply( lambda x: str(TaskStatus.from_value(x)))
            #去重
            df.drop_duplicates(subset=[href_id],inplace=True)
            self.cache_df(album_xlsx_path,sheet_name,df)
            

        
        summary_df=self.export_summary_df()
        if df_empty(summary_df):
            return
        
        
        #矫正下载路径
        with self.logger.raii_target(detail="矫正专辑中的下载路径") as logger:
            
            temp_id="local_audio_path_count"
            temp_df=summary_df[local_path_id].apply(lambda x:normal_path(x).count("/"))
            mask=temp_df==5
            correct_df=summary_df[mask]
            for _,row in correct_df.iterrows():
                url=row[href_id]
                
                album_xlsx_path=Path(row[album_path_id])
                author_name=album_xlsx_path.parent.stem
                
                audio_path=Path(row[local_path_id])
                parts = list(audio_path.parts)
                

                # 插入新目录
                parts.insert(len(parts)-2, author_name)
                dest_path=str(Path(*parts))
                
                
                album_df=self.get_df(album_xlsx_path,audio_sheet_name)
                if df_empty(album_df):
                    continue
                
                result_df=find_rows_by_col_val(album_df,href_id,url)
                if df_empty(result_df):
                    
                    
                    
                    continue
                for album_index,row in result_df.iterrows():
                    album_df.loc[album_index,local_path_id]=dest_path
                #更新数据
                self.cache_df(album_xlsx_path,audio_sheet_name,album_df)
                
                
                self.logger.info("完成",f"{album_xlsx_path}中:{audio_path}->{dest_path}")
        
        #在汇总表中筛选数据，并做其他处理

        
        filter_str="成语"
        
        mask= summary_df[local_path_id].str.contains(filter_str) |summary_df[album_path_id].str.contains(filter_str) |summary_df[album_name_id].str.contains(filter_str) 
        #筛选后结果
        filter_df=summary_df[mask].copy()
        if df_empty(filter_df):
            return
        
        # filter_df=filter_df.drop_duplicates(subset=[album_path_id])
        
        @exception_decorator(error_state=False)
        def _get_author_path(album_path:str):
            album=Path(album_path)
            
            dest=album.parent.parent/f"{album.parent.stem}.xlsx"
            return str(dest)
        
        filter_df["author_path"]=filter_df[album_path_id].apply(_get_author_path)
        
        dfs_dict={}
        
        #按照 _album.xlsx  进行去重处理
        # filter_df.drop_duplicates(subset=[album_path_id],inplace=True)
        
        for _,row in filter_df.iterrows():
            status:TaskStatus=TaskStatus.from_value(row[downloaded_id])
            if status.is_success:
                continue
            url=row[href_id]
            album_xlsx_path=row[album_path_id]
            album_df=self.get_df(album_xlsx_path,audio_sheet_name)
            if df_empty(album_df):
                continue
            # #修改 album_df 的状态
            album_result_df=find_rows_by_col_val(album_df,href_id,url)
            if df_empty(album_result_df):
                self.logger.debug("修改 album_df 的状态失败")
                
                
                continue
            for index,result_row in album_result_df.iterrows():
                album_df.loc[index,downloaded_id]=status.clear_temp_canceled.value
                

            dfs_dict[album_xlsx_path]=album_df

        #清除所有的临时取消 状态
        for _,album_df in dfs_dict.items():
            AudioManager.clear_df_temp_canceled(album_df)
        
        
        #修改 author_df 的状态
        album_path_lst=filter_df[album_path_id].drop_duplicates().tolist()
        for album_xlsx_path in  album_path_lst:
            album_xlsx_path=str(album_xlsx_path)
            author_xlsx_path=_get_author_path(album_xlsx_path)
            author_df=self.get_df(author_xlsx_path,album_id)
            author_result_df=find_rows_by_col_val(author_df,local_path_id,album_xlsx_path)
            if df_empty(author_result_df):
                self.logger.debug("修改 author_df 的状态失败",f"author_xlsx_path:{author_xlsx_path}")
                continue
            for author_index,author_row in author_result_df.iterrows():
                author_status=TaskStatus.from_value(author_row[downloaded_id])
                if author_status.is_success:
                    continue
                author_df.loc[author_index,downloaded_id]=author_status.clear_temp_canceled.value
                
                pass
        def _get_folder(cur_path):
            
                temp_path=Path(cur_path)
                cur_path=str(temp_path.parent/temp_path.stem.replace("_album",""))
                return cur_path.replace("xlsx","audio")
                
                
        self.logger.info(f"筛选'{filter_str}'成功",f"\n{'\n'.join(map(_get_folder,album_path_lst))}\n",update_time_type=UpdateTimeType.STAGE)
        
        
    def clear_temp_cancled(self,xlsx_path):
        for temp_path,sheet_name,df in self.df_lst:
            if not path_equal(temp_path) or df_empty(df):
                continue
            for index,row in df.iterrows():
                status=TaskStatus.from_value(row[downloaded_id]).clear_temp_canceled
                df.loc[index,downloaded_id]=status.value
            pass
        pass
    
    @staticmethod
    def _can_download_df(df)->pd.DataFrame:
        if df_empty(df) :
            return
        mask=df[downloaded_id].apply(lambda x:TaskStatus.from_value(x).can_download)
        return df[mask]
    @staticmethod
    def _can_download_dfs(dfs:list[tuple[str,str,pd.DataFrame]])->list[tuple[str,str,pd.DataFrame]]:
        results=[]
        for xlsx_path,name,album_df in dfs:
            df=AudioManager._can_download_df(album_df)
            if df_empty(df): continue
            results.append((xlsx_path,name,df))
        return results
        

    @property
    def filter_catalog_df(self)->tuple[str,str,pd.DataFrame]:
        if results:= AudioManager._can_download_dfs([self.catalog_df]):
            return results[0]
    
    
    @property
    def filter_author_df(self)->list[tuple[str,str,pd.DataFrame]]:
        return AudioManager._can_download_dfs( self.author_dfs)
    
    @property
    def filter_album_df(self)->list[tuple[str,str,pd.DataFrame]]:
        return AudioManager._can_download_dfs( self.album_dfs)
