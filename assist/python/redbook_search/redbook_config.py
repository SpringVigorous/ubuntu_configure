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

@dataclass
class RedConfig:
    note_type_map: NoteTypeMap
    path: Path
    scroll_to_view_js: str
    listen: Listen
    sync_note_comment: bool
    flag:Flag
    setting: Setting
    