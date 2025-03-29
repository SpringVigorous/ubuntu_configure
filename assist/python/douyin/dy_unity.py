import os
import sys
import re
from pathlib import Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from base import check_dir
#苏州水乡_001.mp4
def info_from_org(org_name:str):
    dest_name=Path(org_name).stem
    series_name,series_number=dest_name.split("_")
    return series_name,series_number


#顾村公园樱花_001-1080x1920_001.mp4
def info_from_dest(dest_path:str):
    
    dest_name=Path(dest_path).stem
    
    org_name,latter=dest_name.split("-")
    series_name,series_number=info_from_org(org_name)
    pixel,scene_number=latter.split("_")
    return series_name,series_number,pixel,scene_number

class OrgInfo:
    def __init__(self,org_name:str) -> None:
        self.series_name,self.series_number=info_from_org(org_name)
        pass
    def __str__(self) -> str:
        return f"OrgInfo({self.series_name},{self.series_number})"

    @property
    def org_name(self):
        return f"{self.series_name}_{self.series_number}"

class DestInfo(OrgInfo):
    def __init__(self,dest_path:str) -> None:
        self.series_name,self.series_number,self.pixel,self.scene_number=info_from_dest(dest_path)
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
    
dy_root=DYRootDir(r"F:\worm_practice\douyin")

if __name__=="__main__":
    # dest_path=r"F:\worm_practice\douyin\素材\org\顾村公园樱花_001-1080x1920_001.mp4"
    dest_path=r"顾村公园樱花_001-1080x1920_001"
    
    
    
    # print(Path(dest_path).stem)
    # exit()
    info=DestInfo(dest_path)
    print(info)