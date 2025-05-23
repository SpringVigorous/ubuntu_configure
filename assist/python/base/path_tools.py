import sys
from pathlib import Path
import os
import system_tools as st
from collect_tools import unique
#track_index:0表示当前文件目录，1表示当前文件的父目录，以此类推
def get_folder_path(dir_path:str,track_index:int=0)->str:
    org_path= Path(dir_path)
    
    is_file=org_path.is_file()
    org_path=org_path.parent if is_file else org_path
    
    while track_index>0:
        org_path=org_path.parent
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

def path_equal(path1:str,path2:str)->bool:
     path1=os.path.normpath(str(Path(path1).resolve()))
     path2=os.path.normpath(str(Path(path2).resolve()))
     if st.is_windows():
        return os.path.normcase(path1)==os.path.normcase(path2)
     return path1==path2


def normal_path(path:str)->str:
    return os.path.normpath(path).replace("\\","/")


def windows_path(path:str)->str:
    normal=normal_path(path)

    return normal.replace("/",r"\\")


def get_all_files_pathlib(directory,include_suffix:list=None):
    """
    获取指定目录下的所有文件的全路径
    :param directory: 目标目录
    :return: 文件全路径列表
    """
    file_paths = []
    for file in Path(directory).rglob('*'):
        org_path=str(file.resolve())
        if include_suffix and not file.suffix in include_suffix:
            continue
        if file.is_file():
            file_paths.append(str(file.resolve()))
    return file_paths


from typing import Callable 

def special_files(dest_dir,func:Callable[[str],bool]=None)->list[str]:
    results=[]
    for root, dirs, files in os.walk(dest_dir):
        for file in files:
            if func and not func(file):
                continue
            results.append(os.path.join(root,file))
    return results

def spceial_suffix_files(dest_dir,suffixs:list[str]|str)->list[str]:
    if isinstance(suffixs,str):
        suffixs=unique([suffixs])
    return special_files(dest_dir,lambda x:Path(x).suffix in suffixs)

def mp4_files(dest_dir)->list[str]:
    return spceial_suffix_files(dest_dir,".mp4")

def json_files(dest_dir)->list[str]:
    return spceial_suffix_files(dest_dir,".json")

def xlsx_files(dest_dir)->list[str]:
    return spceial_suffix_files(dest_dir,".xlsx")

def txt_files(dest_dir)->list[str]:
    return spceial_suffix_files(dest_dir,".txt")
def jpg_files(dest_dir)->list[str]:
    return spceial_suffix_files(dest_dir,".jpg")

def json_files(dest_dir)->list[str]:
    return spceial_suffix_files(dest_dir,".json")


def m3u8_files(dest_dir)->list[str]:
    return spceial_suffix_files(dest_dir,".m3u8")

if __name__ == '__main__':
    print(windows_path(r"F:\test\ubuntu_configure\assist\python\logs\playlist\1.txt"))