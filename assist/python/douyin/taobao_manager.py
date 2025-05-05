import sys

from pathlib import Path
import os
from typing import Callable

root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )

from base import (
    logger_helper,
    UpdateTimeType,
    arabic_numbers,
    priority_read_json,
    xml_tools,
    concat_dfs,
    unique_df,
    download_sync,
    ThreadPool,
    merge_df,
    update_col_nums,
    assign_col_numbers,
    OCRProcessor,
    fix_url,
    concat_unique,
    content_same,
    sub_df,
    set_attr,
    get_attr,
    except_stack,
    exception_decorator,
    
)
import pandas as pd
from taobao_config import *
from taobao_tools  import *
import threading
class tb_manager():
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

            self.logger=logger_helper("taobao_manager")
            
            self._lock = threading.Lock()
            
            self._read_xlsx_df()
        
            # 初始化标志位
            self.__class__._initialized = True
            
    @property
    def shop_df(self)->pd.DataFrame:

        return set_attr(self._shop_df,"name",shop_name)
    
    
    @property
    def product_df(self)->pd.DataFrame:
        return set_attr(self._product_df,"name",product_name)
    
    @property
    def pic_df(self)->pd.DataFrame:
        return set_attr(self._pic_df,"name",pic_name)
    @property
    def ocr_df(self)->pd.DataFrame:
        return set_attr(self._ocr_df,"name",ocr_name)
    
    def __del__(self):
        logger=self.logger
        logger.update_target("保存数据",xlsx_file)
        logger.update_time(UpdateTimeType.STAGE)
        # 清理资源（如关闭文件、释放网络连接等）
        self._save_xlsx_df()
        logger.info("完成",update_time_type=UpdateTimeType.STAGE)
        
        
        
    @classmethod
    def destroy_instance(cls):
        with cls._lock:
            if cls._instance:
                # 手动触发析构函数
                cls._instance = None
                cls._initialized = False
 


    def has_id_val(self,df:pd.DataFrame,id_name:str,id_val):
        with self._lock:

            if df.empty:
                return False
            
            mask=df[id_name]==id_val
            return mask.any()
                    
            
            

    def has_shop_id(self,shopId:str)->bool:
        return self.has_id_val(self.shop_df,shop_id,shopId)
    
    def has_item_id(self,itemId:str)->bool:
        return self.has_id_val(self.product_df,item_id,itemId)
    
    def has_pic_url(self,pic_url:str)->bool:
        return self.has_id_val(self.pic_df,pic_url_id,pic_url)
    
    def has_ocr_id(self,pic_url:str)->bool:
        return self.has_id_val(self.ocr_df,pic_url_id,pic_url)

                    
    def _read_xlsx_df(self):
        
        logger=self.logger
        logger.update_target("读取数据",xlsx_file)
        logger.update_time(UpdateTimeType.STAGE)
        
        if os.path.exists(xlsx_file):
            with pd.ExcelFile(xlsx_file) as reader:
                sheetnames=reader.sheet_names
                def get_df(name:str,str_col_names:list|str=None)->pd.DataFrame:
                    if name not in sheetnames:
                        return pd.DataFrame()
                    df=reader.parse(name)
                    
                    if str_col_names:
                        if isinstance(str_col_names,str):
                            str_col_names=[str_col_names]
                        for col_id in str_col_names:
                            if col_id in df.columns:
                                df[col_id]=df[col_id].astype(str)
                    return df
                with self._lock:
                    self._shop_df = get_df(shop_name,[shop_id,user_id,seller_id])
                    self._product_df = get_df(product_name,[shop_id,item_id])
                    self._pic_df =  get_df(pic_name,[item_id])
                    self._ocr_df=get_df(ocr_name,[item_id])
        else:
            logger.trace("文件不存在",update_time_type=UpdateTimeType.STAGE)
            with self._lock:
                self._shop_df=pd.DataFrame()
                self._product_df=pd.DataFrame()
                self._pic_df=pd.DataFrame()
                self._ocr_df=pd.DataFrame()
        
        logger.info("完成",update_time_type=UpdateTimeType.STAGE)
            
            
    def _save_xlsx_df(self):
        with self._lock:
            with pd.ExcelWriter(xlsx_file,mode="w") as w:
                self._shop_df.to_excel(w, sheet_name=shop_name, index=False)
                self._product_df.to_excel(w, sheet_name=product_name, index=False)
                self._pic_df.to_excel(w, sheet_name=pic_name, index=False)
                self._ocr_df.to_excel(w, sheet_name=ocr_name, index=False)


    #更新：返回 更新后的数据，和新增的数据
    def update_shop_df(self,shop_df:pd.DataFrame)->pd.DataFrame:
        with self._lock:
            self._shop_df,shop_df=self._update_df(self.shop_df,shop_df,keys=[shop_name_id])      
            return shop_df
        
    #更新：返回 更新后的数据，和新增的数据
    def update_product_df(self,product_df:pd.DataFrame):
        with self._lock:
        
            self._product_df,new_df=self._update_df(self.product_df,product_df,keys=[item_id],
                                                arrage_fun=arrage_product_df,
                                                new_data_func=None)
            return new_df
            
            
    #更新：返回 更新后的数据，和新增的数据
    def update_pic_df(self,pic_df:pd.DataFrame):
        logger=self.logger
        with self._lock:
            def _arrage_pic(df:pd.DataFrame)->pd.DataFrame:
                result=self.product_df.set_index(item_id)[num_id].to_dict()
                logger.trace("显示字典对:",f"{result}")
                return arrange_pic(df,result)
            # print(pic_df)
            
            # print(self._pic_df)
                
            self._pic_df,pic_df=self._update_df(self.pic_df,pic_df,keys=[pic_url_id],arrage_fun=_arrage_pic,
                                                new_data_func=None)
            return pic_df
    #返回  【更新后数据，新增的数据】：pd.DataFrame
    def update_ocr_df(self,ocr_df:pd.DataFrame):
        with self._lock:
            
            # print(self.ocr_df)
            # print(ocr_df)
            
            self._ocr_df,ocr_df=self._update_df(self.ocr_df,ocr_df,keys=[ocr_text_id],
                                                arrage_fun=None,
                                                new_data_func=None)
            return ocr_df
    
    @exception_decorator(error_state=False)
    def _update_df(self,
                  org_df:pd.DataFrame,
                  new_df:pd.DataFrame,keys:list|tuple,
                  arrage_fun:Callable[[pd.DataFrame],pd.DataFrame]=None,
                  new_data_func:Callable[[pd.Series],None]=None,
                  )->tuple[pd.DataFrame,pd.DataFrame]:
        df_name=get_attr(org_df,"name")
        org_df=org_df.copy()
        
        logger=self.logger
        logger.update_target("更取数据",df_name)
        logger.update_time(UpdateTimeType.STAGE)
        
        result_df=concat_unique([org_df,new_df],keys=keys)
        if arrage_fun:
            result_df=arrage_fun(result_df)
        
        cut_df=pd.DataFrame()
        
        if not content_same(org_df,result_df):
            cut_df=sub_df(result_df,org_df,keys)

        logger.info("完成",f"新增{len(cut_df)}条记录",update_time_type=UpdateTimeType.STAGE)
        
        
        if new_data_func and not cut_df.empty:
            logger.update_target("处理新增数据",f"共{len(cut_df)}行")
            logger.trace("开始",update_time_type=UpdateTimeType.STAGE)
            
            for index,row in cut_df.iterrows():
                    logger.stack_target(f"处理新增数据:{index}",str(row))
                    logger.update_time(UpdateTimeType.STEP)
                    try:
                        new_data_func(row)
                        logger.info("完成",update_time_type=UpdateTimeType.STEP)
                    except :
                        logger.error("处理异常",except_stack(),update_time_type=UpdateTimeType.STEP)
                    finally:
                        logger.pop_target()
            logger.info("完成",update_time_type=UpdateTimeType.STAGE)
            
        return [result_df,cut_df]


if __name__=="__main__":
    manager=tb_manager()
    from base import read_from_json_utf8_sig
    dir_temp=r"C:\Users\Administrator\Desktop\备份"
    
    pic_df=pd.read_excel(f"{dir_temp}/pic_df.xlsx")
    pic_df1=pd.read_excel(f"{dir_temp}/pic_df1.xlsx") 
    pic_df[item_id]=pic_df[item_id].astype(str)
    pic_df1[item_id]=pic_df1[item_id].astype(str)
    
    shop_json_path=r"F:\worm_practice\taobao\店铺\shop_293825603_1.json"

    shop_dict=org_shop_dict_from_product(read_from_json_utf8_sig(shop_json_path))
    if shop_dict:
        shop_df=pd.DataFrame([shop_dict])
    
    df=manager.update_shop_df(shop_df)
    print(df)
    print(pic_df)
    print(pic_df1)
    
    
    df=manager.update_pic_df(pic_df)
    print(df)
    df=manager.update_pic_df(pic_df1)
    print(df)
    