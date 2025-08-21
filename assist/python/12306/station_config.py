import os

import sys

from pathlib import Path


root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )

from base import exception_decorator,logger_helper,UpdateTimeType,get_consecutive_elements_info,singleton


@singleton
class StationConfig():
    

    def __init__(self,path:str=None,max_transfers:int=3,) -> None:
        self._default_root=r"F:\worm_practice\train_ticket"
        self.logger=logger_helper()
        self.set_root(path)
        self.set_max_transfers(max_transfers)
    def set_max_transfers(self,max_transfers:int=3):
        self._max_transfers=max_transfers
        
        
    def set_root(self,path:str):
        self._root_path=Path(path if path else self._default_root)
        
        
    def result_txt_path(self,start_station,end_station):
        return  self.result_dir/f"{start_station}-{end_station}_routes.txt"
        
    def result_pic_path(self,start_station,end_station):
        return  self.result_dir/f"{start_station}-{end_station}_pic.png"
    @property
    def max_transfers(self):
        return self._max_transfers
    
    # @property
        
    @property
    def train_routines_path(self)->Path:
        return self.data_dir / "routine.pk"
        
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
    

