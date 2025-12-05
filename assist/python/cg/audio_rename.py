import re
from collections import defaultdict
from base import recycle_bin,df_empty
import pandas as pd
from pathlib  import Path
import os
def normalize_filename(filename):
    """
    规范化文件名，去除多余的下划线
    规则：将多个下划线合并为一个，并移除不影响文件名的下划线
    """
    # 1. 移除文件扩展名
    name, ext = filename.rsplit('.', 1)
    
    name=name.replace("_","")
    
    return f"{name}.{ext}"

def find_duplicate_files(filenames):
    """
    找出相同内容但格式不同的文件
    """
    groups = defaultdict(list)
    
    for filename in filenames:
        normalized = normalize_filename(filename)
        groups[normalized].append(filename)
    
    # 只返回有多于一个文件的组
    result = {k: v for k, v in groups.items() if len(v) > 1}
    return result



def main():

    cur_dir=Path(r"E:\旭尧\有声读物\audio\宝宝巴士\奇妙的科普")
    
    df=pd.read_excel(cur_dir/"名称.xlsx",sheet_name="audio")
    if df_empty(df):
        return
    df["size"]=df["size"].astype(int)
    size_dict=df.set_index('name')['size'].to_dict()
    time_dict=df.set_index('name')['time'].to_dict()
        
        
        
    # 测试数据
    filenames =list(df["name"])

    # 找出重复文件
    duplicates = find_duplicate_files(df["name"])
    remove_files=[]
    rename_files=[]
    for normalized, files in duplicates.items():
        files=list(sorted(files,key=lambda x: len(x)))
        file2,file1,*others=files
        if size_dict[file2]>size_dict[file1]:
            rename_files.append((file2,file1))
            remove_files.append(file1)
        else:
            remove_files.append(file2)
            
            
    recycle_bin([cur_dir/file for file in remove_files])
    for old_file,new_file in rename_files:
        
        os.rename(cur_dir/old_file,cur_dir/new_file) 
        
        
        
        
        
        
if __name__ == "__main__":
    main()