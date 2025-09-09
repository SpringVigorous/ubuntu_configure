import requests
import pandas as pd

import os
import sys

from pathlib import Path


root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )

from base import exception_decorator,logger_helper,UpdateTimeType,get_consecutive_elements_info,singleton,df_empty,find_last_value_by_col_val,concat_dfs,unique_df
from train_station import TrainStationManager
from station_config import StationConfig
from datetime import datetime,timedelta
from ticket_url import TicketUrl


@singleton
class PriceManager:
    def __init__(self,date:str=None) -> None:

        self._df:pd.DataFrame=None
        self.logger=logger_helper(self.__class__.__name__)
        self._date=None
        self.set_date(date)
        self.load_df()

        
    def set_date(self,date:str):
        if not date:
            date=(datetime.now()+timedelta(days=3)).strftime("%Y-%m-%d")
        self._date=date.replace(".","-")

        
        
        
    @property
    def date(self):
        return self._date
    
    @property
    def df(self):
        return self._df
        
    def load_df(self):
       config= StationConfig()
       self._df=config.price_df


    def add_df(self,df:pd.DataFrame):       
        config= StationConfig()
        self._df= config.add_price_df(df)

    @exception_decorator(error_state=False)
    def _query_prices_from_url(self,from_station, to_station, train_date)->pd.DataFrame:
        train_date=train_date.replace(".","-")
        return TicketUrl.query_prices(from_station, to_station, train_date)

    @exception_decorator(error_state=False)
    def _query_df_impl(self,df:pd.DataFrame,from_city, to_city)->pd.DataFrame:
        if df_empty(df):
            return
      
        
        result=StationConfig().get_route_key_df(from_city,to_city,df)
        if df_empty(result):            
            return 
        result=result.copy()
        new_names={
            "from_station_name": "出发站", 
            "to_station_name": "到达站",
            "train_no":"编号",
            "station_train_code":"车次",
            "train_type":"类型",
            "start_time":"出发时间",
            "arrive_time":"到达时间",
            "lishi":"耗时",

        }
        
        result.rename(columns=new_names, inplace=True)
        
        return unique_df(result,keys="编号")
    @exception_decorator(error_state=False)
    def query_df(self,from_city, to_city)->dict:
        df= self._query_df_impl(self.df,from_city, to_city)
        if df_empty(df):
            df=self._query_prices_from_url(from_city,to_city,self.date)
            self.add_df(df)
            return self._query_df_impl(self.df,from_city, to_city)
        return df

    @exception_decorator(error_state=False)
    def _query_price_by_df(self,df,train_no,from_station, to_station):
        if df_empty(df) or not train_no:
            return 
        
        condition = (df['train_no'] == train_no) & (df['from_station_name'] == from_station) & (df['to_station_name'] == to_station)
        result = df[condition]['infoAll_list']  # 先筛选行，再选择列M
        if not isinstance(result,str):
            if df_empty(result):
                return
            result = result.values[-1]
        train_manager=TrainStationManager()
        return train_manager.prices(result)
    
    @exception_decorator(error_state=False)
    def query_price(self,train_no,from_station, to_station)->dict:

        result=self._query_price_by_df(self._df,train_no,from_station, to_station)
        if result:
            return result
        #重新获取
        df=self._query_prices_from_url(from_station,to_station,self.date)
        self.add_df(df)
        result=self._query_price_by_df(df,train_no,from_station, to_station)
        if not result:
            self.logger.update_target(detail=f"{train_no}:{from_station}-{to_station}")
            self.logger.warn("未找到")
        
        return result



        
        
        
        
if __name__ == "__main__":

    from_station = "西峡"  # 北京西
    to_station = "合肥"    # 上海虹桥
    train_date = "2025-09-11"
    manager=PriceManager()
    df=manager.query_price(from_station, to_station)
