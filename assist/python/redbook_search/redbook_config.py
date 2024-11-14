from dataclasses import dataclass, asdict
from typing import Dict


@dataclass
class NoteTypeMap:
    all: str
    normal: str
    video: str

@dataclass
class Path:
    search_input_path: str
    search_button_path: str
    close_path: str
    user_path: str
    user_item: str
    user_notes: str
    filter_box: str
    filter_path: str
    note_scroll_path: str
    comments_container_path: str
    comment_content_path: str
    comment_list_path: str
    comment_end_path: str
    comment_more_path: str

@dataclass
class Listen:
    listen_search: str
    listen_note: str
    listen_comment: str
    
    
@dataclass
class Flag:
    title_suffix:list[str]   
    title_prefix:list[str]   
    no_tilte_split:str 
    @property
    def title_suffix_pattern(self):
        return f' - ({"|".join(self.title_suffix)})$'
    @property
    def title_prefix_pattern(self):
        return f'^({"|".join(self.title_prefix)})\n'

@dataclass
class Setting:
    root_path: str
    history_path: str
    note_path: str
    cache_path: str

interact_count:int =0

@dataclass
class SleepTime:
    wait_count:int
    small_interval:int|float
    big_interval:int|float
    common_interval:int|float
    #多少次之后，会出现限制
    limit_count:int
    
    def get_interval(self, count: int):
        sleep_time=self.big_interval if count %self.wait_count ==0 else self.small_interval
        return sleep_time
    def check_limit(self, count: int=1):
        global interact_count
        interact_count+=count
        return (interact_count>self.limit_count,interact_count)

    

@dataclass
class RedConfig:
    note_type_map: NoteTypeMap
    path: Path
    scroll_to_view_js: str
    listen: Listen
    sync_note_comment: bool
    flag:Flag
    setting: Setting
    sleep_time: SleepTime

    