
import os
import sys

def add_path(*args):
    for path in args:
        if path in sys.path:
            continue
        sys.path.append(path)
    # print(sys.path)  
    
    
# 将当前脚本所在项目的根路径添加到 搜索路径 sys.path 中，方便寻找自己编写的包
# 脚本所在目录的上级目录为项目根目录，将其添加到搜索路径中
def add_parent_path_by_file(file_path,*args):
    
    cur_dir=os.path.dirname(file_path)
    cur_path=[os.path.abspath(os.path.join(cur_dir,f"../{arg}")) for arg in args]
    add_path(os.path.dirname(cur_dir),*cur_path)
    # print(sys.path)    


# 脚本所在目录的上级目录为项目根目录，将其添加到搜索路径中
def add_sub_path_by_file(file_path,*args):
    cur_dir=os.path.dirname(file_path)
    cur_path=[os.path.abspath(os.path.join(cur_dir,arg)) for arg in args]
    add_path(os.path.dirname(cur_dir),*cur_path)
    
    