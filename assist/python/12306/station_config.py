import os

import sys

from pathlib import Path
import pandas as pd

root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )

from base import exception_decorator,logger_helper,UpdateTimeType,get_consecutive_elements_info,singleton,df_empty,add_df,recycle_bin,pkl_files,update_df


@singleton
class StationConfig:
    def __init__(self,path:str=None,max_transfers:int=2,) -> None:
        self._default_root=r"F:\worm_practice\train_ticket"
        self.logger=logger_helper()
        self.set_root(path)
        self.set_max_transfers(max_transfers)
        
        self._wait_time=[1,480,60,480]
        self.load_xlsx()
        self.set_dirty(False)
        
        
    def set_dirty(self,is_dirty:bool=True):
        self._is_dirty=is_dirty
        
    @property
    def is_dirty(self):
        return self._is_dirty
    
    
    def set_same_wait_time(self,min_minus:int=1,max_minus:int=480):
        self._wait_time[0], self._wait_time[1]=min_minus,max_minus 
        
        
    def set_diff_wait_time(self,min_minus:int=60,max_minus:int=480):
        self._wait_time[2], self._wait_time[3]=min_minus,max_minus 
        
    @property
    def same_wait_time_min(self):
        return self._wait_time[0]
    @property
    def same_wait_time_max(self):
        return self._wait_time[1]
    @property
    def diff_wait_time_min(self):
        return self._wait_time[2]
    @property
    def diff_wait_time_max(self):
        return self._wait_time[3]
        
        
    def set_max_transfers(self,max_transfers:int=3):
        self._max_transfers=max_transfers
        
        
    def set_root(self,path:str):
        self._root_path=Path(path if path else self._default_root)
        
        
    def result_txt_path(self,start_station,end_station):
        return  self.result_dir/f"{start_station}-{end_station}_routes.txt"
        
    def result_pic_path(self,start_station,end_station):
        return  self.result_txt_path(start_station,end_station).with_suffix(".png")
    
    def result_pkl_path(self,start_station,end_station):
        return  self.result_txt_path(start_station,end_station).with_suffix(".pkl")
    @property
    def max_transfers(self):
        return self._max_transfers
    
    # 清理缓存
    def clear_result_cache(self):
        pkl_lst=pkl_files(self.result_dir)
        if pkl_lst:
            recycle_bin(pkl_lst)


        
    @property
    def data_dir(self):
        result= self._root_path / "data"
        os.makedirs(result,exist_ok=True)
        return result
    @property
    def result_dir(self):
        result= self._root_path / "result"
        os.makedirs(result,exist_ok=True)
        return result   
        

    @property
    def xlsx_path(self):
        return self.data_dir / "12306.xlsx"
    @property
    def city_code_name(self):
        return "站点代码表"
    
    @property
    def train_info_name(self):
        return "车次途径信息"

    @property
    def train_route_name(self):
        return "车次时刻表"
    
    @property
    def price_name(self):
        return "价格"
    def load_xlsx(self):
        cur_path=self.xlsx_path
        if cur_path.exists():
            with pd.ExcelFile(cur_path) as reader:
                sheetnames=reader.sheet_names
                def get_df(name:str)->pd.DataFrame:
                    if name not in sheetnames:
                        return pd.DataFrame()
                    return reader.parse(name)
                self._city_code_df=get_df(self.city_code_name)
                self._train_info_df=get_df(self.train_info_name)
                self._train_route_df=get_df(self.train_route_name)
                self._price_df=get_df(self.price_name)
                #添加 train_type列
                
                # if not(df_empty(self._train_route_df) or df_empty(self._train_info_df)) :
                                        
                #     # 步骤1：从b中构建「编号→类型」的映射（用Series实现，索引为编号，值为类型）
                #     type_map = self._train_route_df.set_index('编号')['类型']

                #     # 步骤2：用a的train_no匹配映射，结果赋给a的train_type列
                #     self._train_info_df['train_type'] = self._train_info_df['train_no'].map(type_map)

                
                
        else:
            self._city_code_df:pd.DataFrame=pd.DataFrame()
            self._train_info_df:pd.DataFrame=pd.DataFrame()
            self._train_route_df:pd.DataFrame=pd.DataFrame()
            self._price_df:pd.DataFrame=pd.DataFrame()

    @exception_decorator(error_state=False)
    def save_xlsx(self):
        cur_path=self.xlsx_path
        logger=logger_helper("保存",cur_path)
        if not self.is_dirty:
            logger.info("未修改，忽略保存")
            return
        
        with pd.ExcelWriter(cur_path) as writer:
            def _save_df(df:pd.DataFrame,name:str):
                if not df_empty(df):
                    df.to_excel(writer,name,index=False)
            _save_df(self._city_code_df,self.city_code_name)      
            _save_df(self._train_info_df,self.train_info_name)
            _save_df(self._train_route_df,self.train_route_name)
            _save_df(self._price_df,self.price_name)
        logger.info("成功",update_time_type=UpdateTimeType.ALL)
    @property
    def city_code_df(self)->pd.DataFrame:
        return self._city_code_df
    
    @property
    def train_info_df(self)->pd.DataFrame:
        return self._train_info_df
    
    @property
    def train_route_df(self)->pd.DataFrame:
        return self._train_route_df
    
    @property
    def price_df(self)->pd.DataFrame:
        return self._price_df


    def add_city_code_df(self,df:pd.DataFrame)->pd.DataFrame:
        self._city_code_df=add_df(df,self.city_code_df,"简拼")
        self.set_dirty(True)
        return self.city_code_df
    def add_train_info_df(self,df:pd.DataFrame)->pd.DataFrame:
        self._train_info_df=add_df(df,self.train_info_df,["train_no","station_no"])
        self.set_dirty(True)
        return self.train_info_df
    def add_train_route_df(self,df:pd.DataFrame)->pd.DataFrame:
        self._train_route_df=add_df(df,self.train_route_df,["编号","出发站","到达站"])
        self.set_dirty(True)
        return self.train_route_df
    
    def add_price_df(self,df:pd.DataFrame)->pd.DataFrame:
        self._price_df=add_df(df,self.price_df,["train_no","from_station_name","to_station_name"])
        self.set_dirty(True)
        return self.price_df
    
    def update_city_code_df(self,df:pd.DataFrame)->pd.DataFrame:
        self._city_code_df=update_df(df,self.city_code_df,"简拼")
        self.set_dirty(True)
        return self.city_code_df
    def update_train_info_df(self,df:pd.DataFrame)->pd.DataFrame:
        self._train_info_df=update_df(df,self.train_info_df,["train_no","station_no"])
        self.set_dirty(True)
        return self.train_info_df
    def update_train_route_df(self,df:pd.DataFrame)->pd.DataFrame:
        self._train_route_df=update_df(df,self.train_route_df,["编号","出发站","到达站"])
        self.set_dirty(True)
        return self.train_route_df
    def update_price_df(self,df:pd.DataFrame)->pd.DataFrame:
        self._price_df=update_df(df,self.price_df,["train_no","from_station_name","to_station_name"])
        self.set_dirty(True)
        return self.price_df
    
    def clear_df(self,df:pd.DataFrame):
        df.drop(df.index,inplace=True)
    
    def clear_city_code_df(self):
        self.clear_df(self._city_code_df)
        self.set_dirty(True)
        
    def clear_train_info_df(self):
        self.clear_df(self._train_info_df)
        self.set_dirty(True)
        
    def clear_train_route_df(self):
        self.clear_df(self._train_route_df)
        self.set_dirty(True)
        
    def clear_price_df(self):
        self.clear_df(self._price_df)
        self.set_dirty(True)

    @property
    def route_col_name(self):
        return "query_key"

    def route_key(self,from_city,to_city):
        return f"{from_city}-{to_city}"
    
    def add_route_key_to_df(self,from_city,to_city,df:pd.DataFrame):
        if df_empty(df): 
            return
        df[self.route_col_name]=self.route_key(from_city,to_city)
    
    def get_route_key_df(self,from_city,to_city,df:pd.DataFrame):
        if df_empty(df): 
            return
        return df[df[self.route_col_name]==self.route_key(from_city,to_city)]
    
if __name__ == "__main__":
    
    lst=[ StationConfig(max_transfers=i+1) for i in range(10)]
    for i in lst:
        print(f"{id(i)}:{i.max_transfers}")

    
