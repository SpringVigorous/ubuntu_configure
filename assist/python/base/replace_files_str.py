from com_log import logger as logger

import os
import fold_tools as fo
import file_tools as fc

import string_tools as st
import com_decorator as dr 
import sys
import path_tools as pt


#仅单个文件
@dr.exception_decorator
def replace_file_str(source_path, dest_path, replace_list_tuple):
    encoding = fc.detect_encoding(source_path)
    fc.replace_content_same_encode(source_path, dest_path, encoding, replace_list_tuple)

#文件夹中所有
@dr.exception_decorator
def replace_dir_str(source_dir, dest_dir, replace_list_tuple):
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

            replace_file_str(org_file_path, dest_file_path,replace_list_tuple)

    return True


if __name__ == "__main__":
    folder=r"F:\test_data\glm"
    list_tuple=[
        ("glm","glm_new"),
        ("GLM","GLM_new")
        ]
    replace_dir_str(folder,os.path.dirname(folder),[("glm","glm_new"),("GLM","GLM_new")])