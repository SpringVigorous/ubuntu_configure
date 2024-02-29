import sys
from pathlib import Path
import os

def get_folder_path(dir_path:str,track_index:int=0):
    while track_index>0:
        dir_path=os.path.dirname(dir_path)
        track_index-=1
    return dir_path

def __add_sys_path_by_dir(dir_path:str,track_index:int=0):
    dir_path=get_folder_path(dir_path,track_index)
    if not os.path.isdir(dir_path):
        return
    if dir_path not in sys.path:
        sys.path.insert(0, dir_path)
    return dir_path


def add_sys_path(file_path:str,track_index:int=0):
    current_file_path = Path(file_path).resolve()
    file_path=str(current_file_path)
    # 获取当前文件所在的目录，并将其添加到sys.path中
    if os.path.isdir(file_path):
        return __add_sys_path_by_dir(file_path,track_index)
    # 获取当前文件的绝对路径
    parent_dir_path = str(current_file_path.parent)
    return __add_sys_path_by_dir(parent_dir_path,track_index)


