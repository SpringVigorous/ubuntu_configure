from typing import Callable,Any
import abc
from base.com_decorator import exception_decorator
from base.com_log import logger_helper,UpdateTimeType
import threading
import pandas as pd
import os
from base.df_tools import get_attr,concat_unique,sub_df,content_same,df_empty,set_attr,read_xlsx_dfs,is_df
from base.except_tools import except_stack
from base.file_tools import sequence_num_file_path

#最好是作为单例
class xlsx_manager(metaclass=abc.ABCMeta):
    sheet_name_flag="name"
    xlsx_path_flag="xlsx_path"
    def __init__(self) -> None:
        self.logger=logger_helper(self.__class__.__name__)
        self.lock = threading.Lock()
        self._df_dict={} #path: list[sheetname,df]
        self._search_dict={}

    def is_first_search(self,xlsx_path:str)->bool:
        if xlsx_path not in self._search_dict:
            self._search_dict[xlsx_path]=1
        else:
            self._search_dict[xlsx_path]+=1
        return self._search_dict[xlsx_path]==1
    def read_dfs(self,xlsx_path:str)->dict[str,pd.DataFrame]:
        logger=self.logger
        xlsx_path=str(xlsx_path)
        
        with self.logger.raii_target("读取数据",xlsx_path) as logger:
            if xlsx_path in self._df_dict:
                if self.is_first_search(xlsx_path):
                    logger.trace("已缓存",update_time_type=UpdateTimeType.STAGE)
                return self._df_dict[xlsx_path]

            if not os.path.exists(xlsx_path):
                logger.debug("文件不存在",update_time_type=UpdateTimeType.STAGE)
                return 

            temp_dict= read_xlsx_dfs(xlsx_path)
            
            for name,df in temp_dict.items():
                self.cache_df(xlsx_path,name,df)
                logger.trace("完成",f'sheet_name:{"|".join(temp_dict.keys())}' ,update_time_type=UpdateTimeType.STAGE)
            
                
            if xlsx_path in self._df_dict:
                return self._df_dict[xlsx_path]
        
        
    @property
    def df_lst(self)->list[tuple[str,str,pd.DataFrame]]:
        
        
        results=[]
        for xlsx_path,df_dict in self._df_dict.items():
            for name,df in df_dict.items():
                results.append((xlsx_path,name,df))
        return results
    
    
    
    
    # 还可以覆盖
    def cache_df(self,xlsx_path:str,sheet_name:str,df:pd.DataFrame):
        xlsx_path=str(xlsx_path)
        if not xlsx_path or not sheet_name or not is_df(df): 
            return
        # if not xlsx_path or not sheet_name or df_empty( df): return
        df=xlsx_manager.set_sheet_name(df,sheet_name) 
        df=xlsx_manager.set_xlsx_path(df,xlsx_path)  
        with self.lock:
            if not self._df_dict.get(xlsx_path): 
                self._df_dict[xlsx_path]={}
            self._df_dict[xlsx_path][sheet_name]=df    

    def get_df(self,xlsx_path:str,sheet_name:str)->pd.DataFrame:
        dfs=self.read_dfs(xlsx_path)
        if not dfs or not sheet_name in dfs: return
        return dfs[sheet_name]

    @exception_decorator(error_state=False)
    def save_dfs(self,xlsx_path:str,dfs:dict[str,pd.DataFrame]):
        @exception_decorator(error_state=False)
        def _save_imp(xlsx_path:str,dfs:dict[str,pd.DataFrame]):
            with self.logger.raii_target("保存数据",xlsx_path) as logger:
                names=[]
                dfs=dict(filter(lambda item: not df_empty(item[1]),dfs.items())  )
                if not dfs: 
                    return True
                #先创建文件夹
                os.makedirs(os.path.dirname(xlsx_path),exist_ok=True)

                with pd.ExcelWriter(xlsx_path,mode="w") as w:                        
                    for sheet_name,df in dfs.items():
                        if  df_empty(df) or not sheet_name:
                            continue
                        df.to_excel(w, sheet_name=sheet_name, index=False)
                        names.append(f"{sheet_name}:共{df.shape[0]}行")
                logger.trace("成功","|".join(names),update_time_type=UpdateTimeType.STEP)
            return True
    
        with self.lock:
            if  _save_imp(xlsx_path,dfs):
                return True
            #备份
            backup_file_path=sequence_num_file_path(xlsx_path)
            success=_save_imp(backup_file_path,dfs)
            
            with self.logger.raii_target("保存数据",backup_file_path) as logger:
                if success: 
                    logger.trace("成功","备份成功",update_time_type=UpdateTimeType.STEP)
                else:
                    logger.error("失败","备份失败",update_time_type=UpdateTimeType.STEP)
            return success

    @abc.abstractmethod
    def before_save(self)->bool:
        return True
    
    
    @exception_decorator(error_state=False)
    def save(self,):
        #保存前处理
        self.logger.update_time(UpdateTimeType.STAGE)
        with self.logger.raii_target("保存前处理") as logger:
            self.before_save()
            logger.info("完成",update_time_type=UpdateTimeType.STAGE)



        with self.logger.raii_target("保存",f"共{len(self._df_dict)}个表") as logger:
            for xlsx_path,dfs in self._df_dict.items():
                if not dfs: 
                    continue
                self.save_dfs(xlsx_path,dfs)
            logger.info("完成",update_time_type=UpdateTimeType.STAGE)
    @staticmethod
    #设置df的sheet_name
    def set_xlsx_path(df:pd.DataFrame,name:Any)->pd.DataFrame:
        return set_attr(df,xlsx_manager.xlsx_path_flag,str(name))

    @staticmethod
    @exception_decorator(error_state=False)
    def get_xlsx_path(df:pd.DataFrame)->Any:
        return get_attr(df,xlsx_manager.xlsx_path_flag)
    
    @staticmethod
    @exception_decorator(error_state=False)
    def get_df_info(df:pd.DataFrame)->str:
        return f"{xlsx_manager.get_xlsx_path(df)}-{xlsx_manager.get_sheet_name(df)}"
    
    
    #df2的信息，赋值给 df1
    @staticmethod
    def clone_info_from(df1:pd.DataFrame,df2:pd.DataFrame):
        if file_path:= xlsx_manager.get_xlsx_path(df2):
            df1=xlsx_manager.set_xlsx_path(df1,file_path)
        if sheet_name:= xlsx_manager.get_sheet_name(df2):
            df1=xlsx_manager.set_sheet_name(df1,sheet_name)
        return df1
    
    
    @staticmethod
    def set_sheet_name(df:pd.DataFrame,name:str)->pd.DataFrame:
        return set_attr(df,xlsx_manager.sheet_name_flag,name)

    @staticmethod
    @exception_decorator(error_state=False)
    def get_sheet_name(df:pd.DataFrame)->str:
        return get_attr(df,xlsx_manager.sheet_name_flag)

    
    
    #添加新数据 + 更新收据
    @exception_decorator(error_state=False)
    def update_df(self,
                  org_df:pd.DataFrame,
                  new_df:pd.DataFrame,
                  keys:list|tuple,
                  arrage_fun:Callable[[pd.DataFrame],pd.DataFrame]=None,
                  new_data_func:Callable[[pd.Series],None]=None,
                  )->tuple[pd.DataFrame,pd.DataFrame]:
        df_info=xlsx_manager.get_df_info(org_df)
        org_df=org_df.copy()
        
        logger=self.logger
        logger.update_target("更新数据",df_info)
        logger.update_time(UpdateTimeType.STAGE)
        
        result_df=concat_unique([org_df,new_df],keys=keys)
        if arrage_fun:
            result_df=arrage_fun(result_df)
        
        cut_df=pd.DataFrame()
        
        if not content_same(org_df,result_df):
            cut_df=sub_df(result_df,org_df,keys)

        logger.debug("完成",f"新增{len(cut_df)}条记录",update_time_type=UpdateTimeType.STAGE)

        if new_data_func and not cut_df.empty:
            logger.update_target("处理新增数据",f"共{len(cut_df)}行")
            logger.trace("开始",update_time_type=UpdateTimeType.STAGE)
            
            for index,row in cut_df.iterrows():
                    logger.stack_target(f"处理新增数据:{index}",str(row))
                    logger.update_time(UpdateTimeType.STEP)
                    try:
                        new_data_func(row)
                        logger.debug("完成",update_time_type=UpdateTimeType.STEP)
                    except :
                        logger.error("处理异常",except_stack(),update_time_type=UpdateTimeType.STEP)
                    finally:
                        logger.pop_target()
            logger.debug("完成",update_time_type=UpdateTimeType.STAGE)
            
            
            
        return [result_df,cut_df]
    
    
