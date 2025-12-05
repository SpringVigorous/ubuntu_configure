from base import TaskStatus,cur_datetime_normal_str
downloaded_id="downloaded"
href_id="href"
album_id="album"
name_id="name"
num_id="num"
url_id="url"
dest_path_id="dest_path"
album_name_id="专辑名称"
title_id="音频标题"
duration_id="时长"
view_count_id="播放量"
release_time_id="发布时间"
local_path_id="local_path"
episode_count_id="集数"
downloaded_count_id="已下载数"
media_url_id="media_url"
parent_xlsx_path_id="parent_xlsx_path"
parent_sheet_name_id="parent_sheet_name"
parent_url_id="parent_url"
album_path_id="album_path"
author_id="author"
album_count_id="专辑数"
suffix_id="suffix"
status_id="status"

create_time_id="create_time"
modify_time_id="modify_time"

xlsx_path_id="xlsx_path"
sheet_name_id="sheet_name"

audio_sheet_name="audio"
album_sheet_name="album"

base_suffix=".m4a"
class AlbumUpdateMsg:

    def __init__(self,xlsx_path:str=None,sheet_name:str=None,url:str=None,status:TaskStatus=TaskStatus.UNDOWNLOADED,suffix:str=".m4a",duration:str="-1",release_time:str="-1",view_count:str="-1",media_url:str=""):
        self._xlsx_path:str=str(xlsx_path)
        self._sheet_name:str=sheet_name
        self._status:TaskStatus=status
        self._suffix:str=suffix
        self._duration:str=duration
        self._release_time:str=release_time
        self._view_count:str=view_count
        self._media_url:str=media_url
        self._local_path:str=None
        self._url:str=url
        
    @property
    def valid(self):
        return self.xlsx_path_valid and self.sheet_name_valid and self.sound_url_valid
    def set_sound_url(self,url:str):
        self._url=url
        
    
    def set_xlsx_path(self,xlsx_path:str):
        self._xlsx_path=str(xlsx_path)
        
    def set_sheet_name(self,sheet_name:str):
        self._sheet_name=sheet_name
        
    def set_status(self,status:TaskStatus):
        self._status=status
        
    def set_suffix(self,suffix:str):
        self._suffix=suffix
        
    def set_duration(self,duration:str):
        self._duration=duration
        
    def set_release_time(self,release_time:str):
        self._release_time=release_time
        
    def set_view_count(self,view_count:str):
        self._view_count=view_count
        
    def set_media_url(self,media_url:str):
        self._media_url=media_url
        
    @property
    def sound_url_valid(self)->bool:
        return bool(self._url)

    @property
    def xlsx_path_valid(self)->bool:
        return bool(self._xlsx_path)
    
    @property
    def sheet_name_valid(self)->bool:
        return bool(self._sheet_name)
    
    @property
    def relase_time_valid(self)->bool:
        return self._release_time and self._release_time !="-1"
    
    @property
    def view_count_valid(self)->bool:
        return self._view_count and self._view_count !="-1"
    
    @property
    def duration_valid(self)->bool:
        return self._duration and self._duration !="-1"
    
    @property
    def media_url_valid(self)->bool:
        return bool(self._media_url)
    @property
    def suffix_valid(self)->bool:
        return bool(self._suffix)
    
    @property
    def release_time_valid(self)->bool:
        return self._release_time and self._release_time !="-1"
    @property
    def sound_url(self)->str:
        return self._url
    @property
    def xlsx_path(self)->str:
        return self._xlsx_path
    @property
    def sheet_name(self)->str:
        return self._sheet_name
    @property
    def status(self)->TaskStatus:
        return self._status
    
    @property
    def suffix(self)->str:
        return self._suffix
    @property
    def duration(self)->str:
        return self._duration
    @property
    def release_time(self)->str:
        return self._release_time
    @property
    def view_count(self)->str:
        return self._view_count
    @property
    def media_url(self)->str:
        return self._media_url
    
    def __repr__(self) -> str:
        
        result={}
        if self.xlsx_path_valid: result["xlsx_path"]=str(self.xlsx_path)
        if self.sheet_name_valid: result["sheet_name"]=self.sheet_name
        if self.sound_url_valid: result["sound_url"]=self.sound_url
        if self.duration_valid: result["duration"]=self.duration

        if self.view_count_valid: result["view_count"]=self.view_count
        if self.media_url_valid: result["media_url"]=self.media_url
        if self.suffix_valid: result["suffix"]=self.suffix

        result.update({
            "status":self.status,

            "release_time":self.release_time,
            
        })
        
        return f"{result}"
    
    
    
    
    
    