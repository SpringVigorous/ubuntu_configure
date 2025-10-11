from typing import Callable
import abc
from base.com_decorator import exception_decorator
from base.com_log import logger_helper,UpdateTimeType
import threading
import pandas as pd
import os
from base.df_tools import get_attr,concat_unique,sub_df,content_same,df_empty,set_attr
from base.except_tools import except_stack




#最好是作为单例
class file_manager(metaclass=abc.ABCMeta):
    sheet_name_flag="name"
    def __init__(self) -> None:
        self.logger=logger_helper(self.__class__.__name__)
        self.lock = threading.Lock()
        self.read_xlsx_df()

    def _read_xlsx_df_imp(self,xlsx_path:str,sheet_names:str|list=None)->list[pd.DataFrame]:
        logger=self.logger
        if not os.path.exists(xlsx_path):
            logger.trace("文件不存在",update_time_type=UpdateTimeType.STAGE)
            return [pd.DataFrame()]
        if not sheet_names:
            return  pd.read_excel(xlsx_path)
        
        
        with pd.ExcelFile(xlsx_path) as reader:
            sheetnames=reader.sheet_names
            def get_df(name:str)->pd.DataFrame:
                if name not in sheetnames:
                    return pd.DataFrame()
                df=reader.parse(name)
                return self._set_df_name(df,name)

            return [ get_df(name)  for  name in sheet_names]
            
    def _save_df_xlsx_imp(self,dfs:list[pd.DataFrame],xlsx_path:str):
        if not dfs: return
        
        logger=self.logger
        dfs=list(filter(lambda x:not df_empty(x),dfs))
        if not dfs: return
        with self.lock:
            with pd.ExcelWriter(xlsx_path,mode="w") as w:
                for df in dfs:
                    if not df_empty(df):
                        df.to_excel(w, sheet_name=self._get_df_name(df), index=False)

        
        
        pass
    def __del__(self):

        # 清理资源（如关闭文件、释放网络连接等）
        self.save_xlsx_df()

            
    @abc.abstractmethod
    def read_xlsx_df(self):
        pass
    
    @abc.abstractmethod
    def save_xlsx_df(self):
        
        
        
        pass
    
    #设置df的sheet_name
    def _set_df_name(self,df:pd.DataFrame,name:str):
        return set_attr(df,file_manager.sheet_name_flag,name)

    def _get_df_name(self,df:pd.DataFrame)->str:
        return get_attr(df,file_manager.sheet_name_flag)
    
    @exception_decorator(error_state=False)
    def _update_df(self,
                  org_df:pd.DataFrame,
                  new_df:pd.DataFrame,
                  keys:list|tuple,
                  arrage_fun:Callable[[pd.DataFrame],pd.DataFrame]=None,
                  new_data_func:Callable[[pd.Series],None]=None,
                  )->tuple[pd.DataFrame,pd.DataFrame]:
        df_name=self._get_df_name(org_df)
        org_df=org_df.copy()
        
        logger=self.logger
        logger.update_target("更新数据",df_name)
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
    
    
