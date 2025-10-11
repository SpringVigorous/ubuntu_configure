import sys
from pathlib import Path
import os
import system_tools as st
from collect_tools import unique
import tempfile
from string_tools import hash_text

temp_root = Path(tempfile.gettempdir()) / "worm_practice"
os.makedirs(temp_root, exist_ok=True)
def cache_temp_path(file_path):
    # 创建临时文件路径
    cur_path=Path(file_path)
    temp_path = temp_root/str(cur_path.with_stem(cur_path.stem + hash_text(file_path)).name)
    return str(temp_path)

def new_path_by_rel_path(org_path,name_latter=None,new_name:str=None,new_stem:str=None,new_suffix:str=None,new_folder=None,rel_cur_index:int=0,keep_rel_path=True):
    root_dir:Path=get_folder_path_by_rel(org_path,rel_cur_index)
    dest_root_dir:Path=root_dir if not new_folder else  root_dir/new_folder


    _new_path=Path(org_path)
    if new_name:
        _new_path=_new_path.with_name(new_name)
    if new_stem:
        _new_path=_new_path.with_stem(new_stem)
    if not(name_latter is None):
        _new_path=_new_path.with_stem(f"{_new_path.stem}{name_latter}")
    if new_suffix:
        _new_path=_new_path.with_suffix(new_suffix)

    dest_path= dest_root_dir/( _new_path.relative_to(root_dir) if keep_rel_path else _new_path.name)
    
    
    if dest_path.is_file():
        os.makedirs(dest_path.parent,exist_ok=True)
    elif dest_path.is_dir():
        os.makedirs(dest_path,exist_ok=True)
    return str(dest_path)
    


#track_index:0表示当前文件目录，1表示当前文件的父目录，以此类推
def get_folder_path_by_rel(dir_path:str,track_index:int=0)->Path:
    
    org_path= Path(dir_path)
    
    lst=list(org_path.parts)
    if not org_path.is_dir():
        lst=lst[:-1]
        
    if  track_index>=len(lst):
        return Path(lst[0])
    elif track_index>0:    
        lst=lst[:len(lst)-track_index]
    return Path(*lst)


def __add_sys_path_by_dir(dir_path:str,track_index:int=0):
    dir_path=get_folder_path_by_rel(dir_path,track_index)
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
     path1=os.path.normpath(os.path.abspath(str(Path(path1).resolve())))
     path2=os.path.normpath(os.path.abspath(str(Path(path2).resolve())))
     if st.is_windows():
        return path1.lower()==path2.lower()
     return path1==path2


def normal_path(path:str)->str:
    return os.path.normpath(path).replace("\\","/")


def windows_path(path:str)->str:
    normal=normal_path(path)
    # return normal
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

def special_files(dest_dir,func:Callable[[str],bool]=None,is_recurse=True)->list[str]:
    results=[]
    
    def _filter_files(files,root):
        for file in files:
            if func and not func(file):
                continue
            results.append(os.path.join(root,file))
    
    
    for root, dirs, files in os.walk(str(dest_dir)):     
        _filter_files(files,root)
        if not is_recurse:
            break
    

            

    return results

def spceial_suffix_files(dest_dir,suffixs:list[str]|str,is_recurse=True)->list[str]:
    if isinstance(suffixs,str):
        suffixs=unique([suffixs])
    return special_files(dest_dir,lambda x:Path(x).suffix in suffixs,is_recurse=is_recurse)

def mp4_files(dest_dir,is_recurse=True)->list[str]:
    return spceial_suffix_files(dest_dir,".mp4",is_recurse=is_recurse)

def json_files(dest_dir,is_recurse=True)->list[str]:
    return spceial_suffix_files(dest_dir,".json",is_recurse=is_recurse)

def xlsx_files(dest_dir,is_recurse=True)->list[str]:
    return spceial_suffix_files(dest_dir,".xlsx",is_recurse=is_recurse)

def txt_files(dest_dir,is_recurse=True)->list[str]:
    return spceial_suffix_files(dest_dir,".txt",is_recurse=is_recurse)
def jpg_files(dest_dir,is_recurse=True)->list[str]:
    return spceial_suffix_files(dest_dir,".jpg",is_recurse=is_recurse)

def pkl_files(dest_dir,is_recurse=True)->list[str]:
    return spceial_suffix_files(dest_dir,".pkl",is_recurse=is_recurse)



img_extensions= [
    # 常见格式
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".webp",
    # 矢量图格式
    ".svg", ".ai", ".eps", ".pdf",  # pdf部分情况下也可视为图片格式
    # 特殊/专业格式
    ".raw", ".cr2", ".nef", ".arw", ".dng", ".orf", ".psd", ".psb",
    ".indd", ".cdr", ".ico", ".jfif", ".pjpeg", ".pjp", ".avif",
    ".heic", ".heif", ".ppm", ".pgm", ".pbm", ".pnm", ".hdr", ".exr"
        ]

def img_files(dest_dir,is_recurse=True)->list[str]:
    return spceial_suffix_files(dest_dir,img_extensions,is_recurse=is_recurse)

def json_files(dest_dir,is_recurse=True)->list[str]:
    return spceial_suffix_files(dest_dir,".json",is_recurse=is_recurse)

def ts_files(dest_dir,is_recurse=True)->list[str]:
    return spceial_suffix_files(dest_dir,".ts",is_recurse=is_recurse)
def m3u8_files(dest_dir,is_recurse=True)->list[str]:
    return spceial_suffix_files(dest_dir,".m3u8",is_recurse=is_recurse)




def is_empty_folder(path):
    if  not os.path.exists(path) or  not os.path.isdir(path):
        return True  # 非目录直接返回非空
    with os.scandir(path) as entries:
        return not any(entries)  # 发现任一条目即返回False


def is_image_file(file_path):
    return Path(file_path).suffix in img_extensions

if __name__ == '__main__':
    org_path=r"F:\test\ubuntu_configure\assist\python\logs\playlist\1.txt"
    # print(windows_path(r"F:\test\ubuntu_configure\assist\python\logs\playlist\1.txt"))
    
    # ls=special_files(r"E:\video\20250804",is_recurse=True)
    # print("\n".join(ls))
    
    
    new_path_by_rel_path(org_path,new_folder="Hello",rel_cur_index=2,keep_rel_path=True)