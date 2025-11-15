import os
import sys
import re
from pathlib import Path

from base import check_dir,special_files,mp4_files
from typing import Callable
#苏州水乡_001.mp4
def info_from_org(org_name:str):
    cur_path=Path(org_name)
    
    dest_name=cur_path.stem
    series_name,series_number,*args=dest_name.split("_")
    return series_name,series_number,cur_path.suffix


#顾村公园樱花_001-1080x1920_001.mp4
def info_from_dest(dest_path:str):
    cur_path=Path(dest_path)
    
    dest_name=cur_path.stem
    
    org_name,latter=dest_name.split("-")
    series_name,series_number,*args=info_from_org(org_name)
    pixel,scene_number=latter.split("_")
    return series_name,series_number,pixel,scene_number,cur_path.suffix

class OrgInfo:
    def __init__(self,org_name:str) -> None:
        self.series_name,self.series_number,self.suffix=info_from_org(org_name)
        pass
    def __str__(self) -> str:
        return f"OrgInfo({self.series_name},{self.series_number})"

    @property
    def org_name(self):
        return f"{self.series_name}_{self.series_number}"

class DestInfo(OrgInfo):
    def __init__(self,dest_path:str) -> None:
        self.series_name,self.series_number,self.pixel,self.scene_number,self.suffix=info_from_dest(dest_path)
        pass
    def __str__(self) -> str:
        return f"DestInfo({self.series_name},{self.series_number},{self.pixel},{self.scene_number})"
    


class DYRootDir:
    def __init__(self,root_path:str=None) -> None:
        self._root_path=""
        self.set_root(root_path)
        pass

    def set_root(self,root_path:str):
        if not root_path:
            return
        self._root_path=os.path.abspath(root_path)
        check_dir(self.dest_root)
        check_dir(self.message_root)
        check_dir(self.org_root)
        check_dir(self.video_create_root)
        check_dir(self.video_cleaned_root)
        check_dir(self.usage_root)
        check_dir(self.usage_src_root)
        check_dir(self.split_info_root)
        check_dir(self.split_src_root)
        check_dir(self.crawl_root)
    
    
    def __str__(self) -> str:
        return f"DYRootDir({self.root_path})"
    
    @property
    def root_path(self)->str:
        return os.path.join(self._root_path,"素材")
    
    @property
    def crawl_root(self)->str:
        return os.path.join(self._root_path,"crawl")
    @property
    def dest_root(self)->str:
        return os.path.join(self.root_path,"dest")


    def dest_sub_dir(self,sub_name)->str:
        dest=os.path.join(self.dest_root,sub_name)
        check_dir(dest)
        return dest
    
    @property
    def message_root(self)->str:
        return os.path.join(self.root_path,"message")
    
    @property
    def message_base_file(self)->str:
        return os.path.join(self.message_root,"wechat_messages.txt")
    
    @property
    def message_json_file(self)->str:
        return os.path.join(self.message_root,"微信消息.json")
    @property
    def message_xls_file(self)->str:
        return os.path.join(self.message_root,"微信消息.xlsx")
    
    @property
    def org_root(self)->str:
        return os.path.join(self.root_path,"org")
    
    @property
    def usage_root(self)->str:
        return os.path.join(self.root_path,"usage")
    
    
    def usage_sub_dir(self,sub_name)->str:
        dest_dir=os.path.join(self.usage_root,sub_name)
        check_dir(dest_dir)
        return dest_dir
    
    @property
    def usage_src_root(self)->str:
        return os.path.join(self.root_path,"usage_src")
    
    @property
    def video_create_root(self)->str:
        return os.path.join(self.root_path,"create")
    
    
    @property
    def video_cleaned_root(self)->str:
        return os.path.join(self.root_path,"cleaned")
    
    
    @property
    def split_info_root(self)->str:
        return os.path.join(self.root_path,"split_info")
    
    @property
    def split_src_root(self)->str:
        return os.path.join(self.root_path,"split_src")

    def usage_src_path(self,file_name="1.json")->str:
        return os.path.join(self.usage_src_root,f"{Path(file_name).stem}.json")
    
    @property
    def split_info_xlsx_path(self)->str:
        return os.path.join(self.split_info_root,"视频分割信息.xlsx"),"视频信息"
    
    @property
    def usage_info_xlsx_path(self)->str:
        return os.path.join(dy_root.usage_src_root,"视频使用信息.xlsx"),"视频信息"

    
    @property
    def temp_dir(self)->str:  # 定义一个名为temp_dir的方法，该方法属于某个类，返回类型为字符串
        return os.path.join(self._root_path,"temp")  # 使用os.path.join方法将类的私有属性_root_path与字符串"temp"拼接，返回拼接后的路径字符串

    @property
    def similarity_dir(self)->str:  # 定义一个名为temp_dir的方法，该方法属于某个类，返回类型为字符串
        return os.path.join(self.root_path,"similarity")  # 使用os.path.join方法将类的私有属性_root_path与字符串"temp"拼接，返回拼接后的路径字符串

    @staticmethod
    def video_filename(name):
        return f"{name}.mp4"
    
    

    def org_mp4_paths(self):
        return mp4_files(self.org_root)
        

    def dest_mp4_paths(self,name:str):
        cur_dir=self.dest_sub_dir(name)
        has_series= "_" in name
        
        if has_series:
            info=OrgInfo(name)
            cur_dir=self.dest_sub_dir(info.series_name)
        files=mp4_files(cur_dir)
        if not has_series:
            return files
        return [file for file in files if DestInfo(file).org_name == name]

    
from base import worm_root

    
    
dy_root=DYRootDir(worm_root/r"douyin")

if __name__=="__main__":
    # dest_path=worm_root/r"douyin\素材\org\顾村公园樱花_001-1080x1920_001.mp4"
    dest_path=r"顾村公园樱花_001-1080x1920_001"
    
    
    
    # print(Path(dest_path).stem)
    # exit()
    info=DestInfo(dest_path)
    print(info)