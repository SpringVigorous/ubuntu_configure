from com_log import logger as logger

import os
import fold_tools as fo
import file_tools as fc

import string_tools as st
import com_decorator as dr 
import sys
import path_tools as pt
from pathlib import Path
import re

from enum import Enum

class CoverType(Enum):
    FORCE_COVER = 'force_cover'
    NO_COVER = 'no_cover'
    NEW_FILE = 'new_file'

    # 自定义方法
    def describe(self):
        descriptions = {
            'force_cover': '强制覆盖',
            'no_cover': '不覆盖',
            'new_file': '新建文件'
        }
        return descriptions.get(self.value, '未知')




#部分功能整理到 F:\test\ubuntu_configure\assist\python\integer\alter_encoding.py
#仅单个文件
@dr.exception_decorator()
def replace_file_str(source_path, dest_path, replace_list_tuple,covere_type:CoverType=CoverType.NEW_FILE):
    if os.path.exists(dest_path):
        if covere_type==covere_type.NO_COVER:
            logger.info(f"已存在：{dest_path},不进行替换")
            return
        elif covere_type==CoverType.NEW_FILE:
            org_dest=Path(dest_path)
            clone_dest=org_dest.parent.joinpath(org_dest.stem+"_new"+org_dest.suffix)
            logger.info(f"已存在：{dest_path},不进行替换，更改文件名为{clone_dest}")
            dest_path=str(clone_dest) 

    
    encoding = fc.detect_encoding(source_path)
    fc.replace_content_same_encode(source_path, dest_path, encoding, replace_list_tuple)

#文件夹中所有
@dr.exception_decorator()
def replace_dir_str(source_dir, dest_dir, replace_list_tuple,cover_type:CoverType=CoverType.NO_COVER):
    # 遍历文件夹

    org_base_dir=os.path.basename(source_dir)
    if not (os.path.exists(source_dir) and os.path.isdir(source_dir))  :
        if logger:
            logger.error(f"源文件夹不存在：{source_dir}")
        return False
    
    folder_name =st.replace_list_tuple_str(org_base_dir,replace_list_tuple)
    dest_dir=os.path.join(dest_dir,folder_name)
    if pt.path_equal(source_dir,dest_dir):
        fo.clear_folder(dest_dir)
    for root, dirs, files in os.walk(source_dir):
        # 构建输出文件路径
        relative_path = st.replace_list_tuple_str(os.path.relpath(root, source_dir),replace_list_tuple)
        dest_dir_path = os.path.abspath(os.path.join(dest_dir, relative_path)) 
        for file in files:

            org_file_path = os.path.join(root, file)
            os.makedirs(dest_dir_path, exist_ok=True)
            # file_extension=os.path.splitext(org_file_path)
            # dest_file_path=os.path.join(dest_dir_path, st.replace_list_tuple_str(file_extension[0],replace_list_tuple)+file_extension[1])
            dest_file_path=os.path.join(dest_dir_path, st.replace_list_tuple_str(file,replace_list_tuple))

            replace_file_str(org_file_path, dest_file_path,replace_list_tuple,cover_type)

    return True
#文件夹中所有
@dr.exception_decorator()
def clone_dir_str(source_dir, dest_dir, replace_list_tuple,clone_list_tuple,cover_type:CoverType=CoverType.NO_COVER):
    # 遍历文件夹

    org_base_dir=os.path.basename(source_dir)
    if not (os.path.exists(source_dir) and os.path.isdir(source_dir))  :
        if logger:
            logger.error(f"源文件夹不存在：{source_dir}")
        return False
    
    folder_name =st.replace_list_tuple_str(org_base_dir,replace_list_tuple)
    dest_dir=os.path.join(dest_dir,folder_name)
    if pt.path_equal(source_dir,dest_dir):
        fo.clear_folder(dest_dir)
    for root, dirs, files in os.walk(source_dir):
        # 构建输出文件路径
        
        
        relative_path = st.replace_list_tuple_str(os.path.relpath(root, source_dir),replace_list_tuple)
        dest_dir_path = os.path.normpath(os.path.join(dest_dir, relative_path)) 
        for file in files:
            org_file_path = os.path.join(root, file)
            os.makedirs(dest_dir_path, exist_ok=True)
            
            def replace_imp(dest_file,replace_list_tuple):
                dest_file_path=os.path.join(dest_dir_path, st.replace_list_tuple_str(dest_file,replace_list_tuple))
                replace_file_str(org_file_path, dest_file_path,replace_list_tuple,cover_type)
            
            dest_files=[]
            if clone_list_tuple:
                for pattern,clone_files,*extra in clone_list_tuple:
                    if not clone_files:
                        continue
                    matches=re.match(pattern, file)
                    if matches:
                        pre=matches.group(1)
                        org_name = matches.group(2)
                        extension = matches.group(3)
                        for clone_file_name in clone_files:
                            dest_file=f"{pre}{clone_file_name}.{extension}"
                            dest_replace=[(org_name,clone_file_name,*extra)] + replace_list_tuple
                            replace_imp(dest_file,dest_replace)

                        break


            replace_imp(file,replace_list_tuple)
            # dest_file_path=os.path.join(dest_dir_path, st.replace_list_tuple_str(file,replace_list_tuple))
            # replace_file_str(org_file_path, dest_file_path,replace_list_tuple,cover_type)

    return True




if __name__ == "__main__":
    
    
    folder=r"F:\test_data\glm"
    list_tuple=[
        ("project_template","dynamic_runtime1"),
        ]
    # replace_file_str(file_path,file_path,list_tuple)
    # replace_dir_str(folder,os.path.dirname(folder),list_tuple)
    
    org_path=r"F:/test/cmake_project/src/project_template"
    dest_path=r"F:/test/cmake_project/src"
    
    clone_list_tuple=[
        (r"(.*?)(class_template)\.(h|cpp|hpp)$",["hello1","hello2","hello3"],True,True),
        ]
    

    clone_dir_str(org_path,dest_path,list_tuple,clone_list_tuple)
    
    
    