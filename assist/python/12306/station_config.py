import os

import sys

from pathlib import Path


root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )

from base import exception_decorator,logger_helper,UpdateTimeType,get_consecutive_elements_info,singleton


@singleton
class StationConfig():
    def __init__(self,path:str=None,max_transfers:int=2,) -> None:
        self._default_root=r"F:\worm_practice\train_ticket"
        self.logger=logger_helper()
        self.set_root(path)
        self.set_max_transfers(max_transfers)
        
        self._wait_time=[1,480,60,480]
        
        
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
    @property
    def max_transfers(self):
        return self._max_transfers
    
    # @property
        
    @property
    def train_routines_path(self)->Path:
        return self.data_dir / "routine.pkl"
        
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
    def station_city_path(self):
        return self.data_dir / "station_city.json"
    
    
    @property
    def station_code_path(self):
        return self.data_dir / "station_code.json"
    
    @property
    def train_ticket_path(self):
        return self.data_dir / "train_ticket.xlsx"
    

if __name__ == "__main__":
    
    lst=[ StationConfig(max_transfers=i+1) for i in range(10)]
    for i in lst:
        print(f"{id(i)}:{i.max_transfers}")

    
    # station_config = StationConfig()
    # print(station_config.station_city_path)
    # print(station_config.station_code_path)
    # print(station_config.train_ticket_path)