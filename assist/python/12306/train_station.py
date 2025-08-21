


import pandas as pd
import requests
import json
import os

import sys

from pathlib import Path
from collections.abc import Iterable

root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )

from base import df_empty,singleton,exception_decorator
from station_config import StationConfig

station_config=StationConfig()
from urllib.parse import quote

# 由于火车站使用三字码，所以我们需要先获取站点对应的三字码
def _station_df_by_url()-> pd.DataFrame:
    code_url = r"https://kyfw.12306.cn/otn/resources/js/framework/station_name.js"
    response = requests.get(code_url)
    response.encoding = 'utf-8'
    code_data = response.text
    # 处理每个匹配项，按 | 分割
    ls=code_data.split("@")[1:]
    # 处理每个匹配项，按 | 分割
    result = [match.split('|') for match in ls if match]
    df = pd.DataFrame(result)
    header=['简拼','站名','编码','全拼','缩称','站编号','城市编码','城市','国家拼音','国家','英文']
    df.columns = header
    return df

def _station_df_by_file(filepath)-> pd.DataFrame:
    
    return pd.read_excel(filepath) if os.path.exists(filepath) else pd.DataFrame()

def _station_df(filepath):
    df=_station_df_by_file(filepath)
    if df_empty(df):
        df=_station_df_by_url()
    return df
    
@singleton
class TrainStationManager:
    
    def __init__(self,station_path:str=station_config.train_ticket_path):
        self._station_xlsx_path=station_path
        os.makedirs(self.root_path,exist_ok=True)
        self._df=_station_df(self._station_xlsx_path)
        self._station_code_path=os.path.join(self.root_path,station_config.station_code_path.name)
        self._station_city_path=os.path.join(self.root_path,station_config.station_city_path.name)

        self._station_code:dict={}
        self._station_city:dict={}
        self._city_station:dict={}
        
        
        self._code_station:dict={}
    
    @property
    def xlsx_path(self):
        return self._station_xlsx_path
    
    @property
    def df(self):
        return self._df
    @property
    def root_path(self):
        return os.path.dirname(self.xlsx_path)
    @property
    def empty(self):
        return df_empty(self._df)

    @exception_decorator(error_state=False)
    def save_to_excel(self):
        # 将结果输出到Excel文件
        if  self.empty:
            return
        self._df.to_excel(self.xlsx_path, index=False)

    @property
    def station_code_dict(self)->dict:
        if not self._station_code:
            self._station_code=self.import_from_json(self._station_code_path) or self._df.set_index('站名').to_dict()['编码']
        return self._station_code

    @property
    def code_station_dict(self)->dict:
        if not self._code_station:
            self._code_station={v: k for k, v in self.station_code_dict.items()}
        return self._code_station
    
    @property
    def station_city_dict(self)->dict:
        
        if not self._station_city:
            self._station_city=self.import_from_json(self._station_city_path) or self._df.set_index('站名').to_dict()['城市']
        return self._station_city
        
    @property
    def city_station_dict(self)->dict:
        if not self._city_station:
            result={}
            for station,city in self.station_city_dict.items():
                if city not in result:
                    result[city]=[station]
                else:
                    result[city].append(station)
            self._city_station=result
        return self._city_station
        
    def get_station_city(self,station)->str:
        return self.station_city_dict.get(station,None) 
    
    
    def _is_big_city_station(self,station)->bool:
        city=self.get_station_city(station)
        if not city:
            return False
        return city in station
    
    def _is_same_city(self,station1,station2)->bool:
        
        if station1==station2:
            return True
        if not self.get_station_city(station1)==self.get_station_city(station2):
            return False
        return  self._is_big_city_station(station1) and self._is_big_city_station(station2)
            
        
        
    
    
    def is_same_city(self,*stations)->bool:
        if not stations:
            return False
        if len(stations)<2:
            return True
        
        return all(self._is_same_city(stations[0],item) for item in stations[1:])

    def export_station_code(self):
        self.export_to_json(self.station_code_dict,self._station_code_path)
        
    def export_station_city(self):
        self.export_to_json(self.station_city_dict,self._station_city_path)    
        
    
    @staticmethod
    def export_to_json(data_dict:dict,filepath):
        if not data_dict:
            return
        with open(filepath,'w',encoding='utf-8') as f:
            json.dump(data_dict,f,ensure_ascii=False,indent=4)
    
    
    @staticmethod
    def import_from_json(filepath)->dict:
        if not os.path.exists(filepath):
            return 
        with open(filepath,'r',encoding='utf-8') as f:
            return json.load(f)

    
    def code_from_city(self,city_name:str)->str:
        return self.station_code_dict.get(city_name,None)
    
    def city_from_code(self,code:str)->str:
        return self.code_station_dict.get(code,None)

    def city_url_param(self,city)->str:
        return f"{quote(city,encoding="utf-8")},{self.code_from_city(city)}"
        
        
    def city_cookie_param(self,city):
        """
        将汉字和对应拼音转换为指定格式的字符串
        格式：汉字的%uUnicode编码 + %2C + 拼音首字母大写缩写
        
        参数:
            chinese_char: 汉字字符串（如"固定"）
            pinyin: 对应拼音，以空格分隔每个字的拼音（如"gu ding"）
        
        返回:
            格式化字符串（如"%u56FA%u59CB%2CGD"）
        """
        # 1. 处理汉字：转换为%uXXXX格式的Unicode编码
        chinese_encoded = []
        for char in city:
            # 获取字符的Unicode码点（十进制），转换为4位十六进制（大写）
            unicode_hex = format(ord(char), '04X')  # 确保结果为4位，不足补0
            chinese_encoded.append(f'%u{unicode_hex}')
        chinese_part = ''.join(chinese_encoded)
        
        # 2. 处理拼音：提取每个字拼音的首字母并大写
        # 按空格分割拼音（假设输入格式为"字1拼音 字2拼音"）
        
        pinyin_part = self.code_from_city(city)

        
        # 3. 用%2C（逗号的URL编码）连接两部分
        return f'{chinese_part}%2C{pinyin_part.upper()}' if chinese_part and pinyin_part else ''


if __name__ == '__main__':
    # all_to_file('station_names.xlsx')
    # names_to_json("city.json")
    info =TrainStationManager()
    info.save_to_excel()
    info.export_station_code()
    info.export_station_city()
    
    print(info.get_station_city("上海"))
    print(info.is_same_city("上海","安亭北","金山北"))
   
