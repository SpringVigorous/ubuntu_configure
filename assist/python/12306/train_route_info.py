from threading import Thread

import pandas as pd

import os


import sys

from pathlib import Path
from datetime import datetime

root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )

from base import exception_decorator,logger_helper,UpdateTimeType,arabic_numbers,unique,pickle_dump,pickle_load,df_empty,singleton
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
        
        if df_empty(self.df):
            return 
        df=self.df
        condition=(df["出发站"]==from_city)& (df['到达站'] == to_city)
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
        