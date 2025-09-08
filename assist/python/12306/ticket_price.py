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



@singleton
class PriceManager:
    def __init__(self,date:str=None) -> None:

        self.df:pd.DataFrame=None
        self.logger=logger_helper(self.__class__.__name__)
        self._date=None
        self.set_date(date)
        self.load_df()
        
        # print(self)
        
    def set_date(self,date:str):
        if not date:
            date=(datetime.now()+timedelta(days=3)).strftime("%Y-%m-%d")
        self._date=date
        
        
        
    @property
    def date(self):
        return self._date
    
    @property
    def xlsx_path(self):
        return StationConfig().result_dir / f"price_{self.date}.xlsx"
    
    @exception_decorator(error_state=False)
    def export_df(self):
        self.df.to_excel(self.xlsx_path)
        
        
    def load_df(self):
        self.df=pd.read_excel(self.xlsx_path) if self.xlsx_path.exists() else pd.DataFrame()

    def add_df(self,df:pd.DataFrame):
        if df_empty(df):
            return
        if df_empty(self.df):
            self.df=df
            return
        
        self.df= unique_df(concat_dfs([self.df,df]),keys=["train_no","from_station_name","to_station_name"])
       


    def _query_prices_from_url(self,from_station, to_station, train_date)->pd.DataFrame:
        train_date=train_date.replace(".","-")
        
        station_manager=TrainStationManager()

        from_station_no =station_manager.code_from_city(from_station)  # 北京西
        to_station_no = station_manager.code_from_city(to_station)     # 上海虹桥
        
        from_url_cookie=station_manager.city_cookie_param(from_station)
        to_url_cookie=station_manager.city_cookie_param(to_station)
        cookies = {
            'JSESSIONID': '32AA71172EAC0D2A681FA19A5D0AA4C5',
            '_jc_save_wfdc_flag': 'dc',
            '_jc_save_zwdch_fromStation': '%u56FA%u59CB%2CGXN',
            '_jc_save_zwdch_cxlx': '0',
            '_c_WBKFRo': 'sraC6YRdJb6MbjH9xxa1sLa6fYmljIB032VpIYoS',
            'OUTFOX_SEARCH_USER_ID_NCOO': '742496979.536112',
            'BIGipServerotn': '1658388746.24610.0000',
            'BIGipServerpassport': '820510986.50215.0000',
            'guidesStatus': 'off',
            'highContrastMode': 'defaltMode',
            'cursorStatus': 'off',
            'route': 'c5c62a339e7744272a54643b3be5bf64',
            '_jc_save_toDate': train_date,
            '_jc_save_fromStation': from_url_cookie,
            '_jc_save_toStation': to_url_cookie,
            '_jc_save_fromDate': train_date,
            '_jc_save_fromStation': from_url_cookie,
            '_jc_save_toStation': to_url_cookie,
            '_jc_save_fromDate': train_date,
        }

        headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            # 'Cookie': 'JSESSIONID=32AA71172EAC0D2A681FA19A5D0AA4C5; _jc_save_wfdc_flag=dc; _jc_save_zwdch_fromStation=%u56FA%u59CB%2CGXN; _jc_save_zwdch_cxlx=0; _c_WBKFRo=sraC6YRdJb6MbjH9xxa1sLa6fYmljIB032VpIYoS; OUTFOX_SEARCH_USER_ID_NCOO=742496979.536112; BIGipServerotn=1658388746.24610.0000; BIGipServerpassport=820510986.50215.0000; guidesStatus=off; highContrastMode=defaltMode; cursorStatus=off; route=c5c62a339e7744272a54643b3be5bf64; _jc_save_toDate=2025-09-08; _jc_save_fromStation=%u897F%u5CE1%2CSNH; _jc_save_toStation=%u5408%u80A5%2CHFH; _jc_save_fromDate=2025-09-10; _jc_save_fromStation=%u897F%u5CE1%2CSNH; _jc_save_toStation=%u5408%u80A5%2CHFH; _jc_save_fromDate=2025-09-10',
            'Referer': 'https://kyfw.12306.cn/otn/view/queryPublicIndex.html',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.97 Safari/537.36 SE 2.X MetaSr 1.0',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Not)A;Brand";v="24", "Chromium";v="116"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        params = {
            'leftTicketDTO.train_date': train_date,
            'leftTicketDTO.from_station': from_station_no,
            'leftTicketDTO.to_station': to_station_no,
            'purpose_codes': 'ADULT',
        }

        response = requests.get(
            'https://kyfw.12306.cn/otn/leftTicketPrice/queryAllPublicPrice',
            params=params,
            cookies=cookies,
            headers=headers,
        )
        datas=[item["queryLeftNewDTO"] for item in response.json()["data"]]
        df=pd.DataFrame(datas)
        if not df_empty(df):
            df["date"]=self.date

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

        result=self._query_price_by_df(self.df,train_no,from_station, to_station)
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
