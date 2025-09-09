from threading import Thread

import pandas as pd

import os


import sys

from pathlib import Path
from datetime import datetime

root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )

from base import exception_decorator,logger_helper,UpdateTimeType,arabic_numbers,unique,pickle_dump,pickle_load,df_empty,singleton,find_last_value_by_col_val,find_values_by_col_val
from station_config import StationConfig


@singleton
class TrainInfoManager:
    def __init__(self):
        self.load_df()
    def load_df(self):
        config= StationConfig()
        self._train_info_df=config.train_info_df
        
    @property
    def df(self):
        return self._train_info_df
        
    def train_info_by_url(self,train_no):
        
        if df_empty(self.df):
            return 
        df=self.df
        condition=(df["train_no"]==train_no)
        result=df[condition]
        return result
        
    def train_info(self,train_no,date):
        df= self.train_info_by_url(train_no)
        if df_empty(df):
            from ticket_url import TicketUrl
            config= StationConfig()
            df= TicketUrl.query_train_info(train_no,date)
            self.train_route_df=config.add_train_info_df(df)
        return df

    @exception_decorator(error_state=False)
    def train_name(self,train_no)->str:
        if df_empty(self.df):
            return 
        return "/".join(unique(find_values_by_col_val(self.df,"train_no",train_no,"station_train_code").tolist()))
    
    @exception_decorator(error_state=False)
    def train_no(self,train_name):
        if df_empty(self.df):
            return
        return find_last_value_by_col_val(self.df,"station_train_code",train_name,"train_no")
    

    @exception_decorator(error_state=False)
    def train_dfs(self)->dict[str,pd.DataFrame]:
        df=self.df.copy()
        if df_empty(df):
            return
        
        # 1. 将station_no列转换为整数类型（处理可能的字符串格式）
        df['station_no'] = df['station_no'].astype(int)
        
        # 2. 按train_no分组，并初始化结果列表
        grouped = df.groupby('train_no', group_keys=False)  # group_keys=False避免分组键作为索引
        result_dict = {}
        
        # 3. 遍历每个分组，排序后添加到列表
        for train_no, group in grouped:
            # 按station_no升序排序
            sorted_group = group.sort_values(by='station_no', ascending=True)
            # 保留train_no列（分组后该列值相同，但会自动保留）
            result_dict[train_no]=sorted_group
        
        return result_dict

    
    
    
    
@singleton
class TrainRouteManager:
    def __init__(self):
        self.load_df()

    def load_df(self):
        config= StationConfig()
        self._train_route_df=config.train_route_df
        
    @property
    def df(self):
        return self._train_route_df
    def _train_route_by_df(self,from_city,to_city):
        from train_station import TrainStationManager
        if df_empty(self.df) :
            return 
        
        station_manager=TrainStationManager()
        #类似于模糊查找，先查找对应城市，再获取城市有哪些站点
        from_stations=station_manager.city_stations(station_manager.get_station_city(from_city))
        to_stations=station_manager.city_stations(station_manager.get_station_city(to_city))
        
        if not from_stations or not to_stations:
            return
        
        df=self.df
        condition=(df["出发站"].isin(from_stations)& (df['到达站'].isin(to_stations)))
        result=df[condition]
        return result
        
    def train_route(self,from_city,to_city,date):
        df= self._train_route_by_df(from_city,to_city)
        if df_empty(df):
            from ticket_url import TicketUrl
            config= StationConfig()
            df= TicketUrl.query_rest_ticket(from_city,to_city,date)
            self._train_route_df=config.add_train_route_df(df)
        return df
        
    @exception_decorator(error_state=False)
    def train_name(self,train_no):
        if df_empty(self.df):
            return 
        return find_last_value_by_col_val(self.df,"编号",train_no,"车次")
    
    @exception_decorator(error_state=False)
    def train_no(self,train_name):
        if df_empty(self.df):
            return
        return find_last_value_by_col_val(self.df,"车次",train_name,"编号")