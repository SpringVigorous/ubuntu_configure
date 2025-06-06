﻿
from redbook_config import *
import json
from dataclasses import  asdict

#路径为空，则为默认值
def load_config(config_path: str=None) -> RedConfig:
    
    if not config_path :
        from os import path
        cur_path=path.abspath(__file__)
        config_path=path.join(path.dirname(cur_path),"redbook_setting.json")
    
    with open(config_path, 'r',encoding="utf-8-sig") as f:
        config_dict = json.load(f)
    
    # 将字典转换为相应的数据类实例
    note_type_map = NoteTypeMap(**config_dict['note_type_map'])
    path = Path(**config_dict['path'])
    listen = Listen(**config_dict['listen'])
    flag = Flag(**config_dict['flag'])
    setting=Setting(**config_dict['setting'])
    sleep_time=SleepTime(**config_dict['sleep_time'])
    
    # 初始化 RedConfig 实例
    config = RedConfig(
        note_type_map=note_type_map,
        path=path,
        scroll_to_view_js=config_dict['scroll_to_view_js'],
        listen=listen,
        sync_note_comment=config_dict['sync_note_comment'],
        flag=flag,
        setting=setting,
        sleep_time=sleep_time
    )
    
    return config
    
def save_config(config: RedConfig, config_path: str):
    with open(config_path, 'w') as f:
        json.dump(asdict(config), f, indent=4)
        
        
redbook_config:RedConfig=load_config()
time_info:SleepTime=redbook_config.sleep_time
redbook_setting:Setting=redbook_config.setting
note_type_map:NoteTypeMap=redbook_config.note_type_map
web_path:Path=redbook_config.path
web_listen:Listen=redbook_config.listen
content_flag:Flag=redbook_config.flag
sync_note_comment:bool=redbook_config.sync_note_comment


if __name__=='__main__':


    save_config(redbook_config,"redbook_setting.json")
    

    