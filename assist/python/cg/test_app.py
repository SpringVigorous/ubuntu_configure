import re
import os
from collections import defaultdict
from base import move_file,mp3_files,unique,format_count
import pandas as pd
from pathlib import Path
def move_mp3_files(src_dir,dest_dir):
    files=mp3_files(src_dir)
    for file in files:
        move_file(file,dest_dir)
# 楞严经第393讲（第十六套 ) 五十种阴魔

ignore_suffix_num_patterns = [
            # 中文括号数字后缀：（一）、（二）等
            (r'第\d+讲\s*[（(]\s*第[一二三四五六七八九十0-9]+套\s*[）)]\s*',"-"),
            (r'[（(][一二三四五六七八九十零百千万0-9]+[）)]-[\d]-[\d]+$',""),
            (r'[（(][一二三四五六七八九十零百千万0-9]+[）)]-[\d]+$',""),
            # 数字后缀：1, 2, 01, 001等
            (r'[\d]-*[\d]+$',""),
            (r'-*[\d]+$',""),

            # 中文括号数字后缀：（一）、（二）等
            (r'\d*\s*[（(]\s*[一二三四五六七八九十零百千万0-9]+\s*[）)]\s*$',""),
  
            # "之X"格式后缀：之1、之2、之一、之二等
            (r'之[一二三四五六七八九十0-9]+$',""),
    ]
def remove_suffix( text):
    """去除字符串中的各种后缀"""
    
    for pattern,seg in ignore_suffix_num_patterns:
        # 使用正则表达式匹配并替换后缀
        result = re.sub(pattern, seg, text)
        # 如果替换后字符串不为空，且与原来不同，则使用替换结果
        if result and result != text:
            text = result
    
    return text.strip()

            
            
            
pre_num_compilers = [re.compile(r'^[\d]+-[\d]+(.*)'),
                     re.compile(r'^[\d]+-(.*)')]
def ignore_pre_num_and_suffix(name:str):
    name=Path(name).stem
    for pre_num_compiler in pre_num_compilers:
        if match:=pre_num_compiler.match(name):
            return match.group(1)

    return name

local_path_id="local_path"
name_id="name"

catalog_id="catalog"
main_catalog_id="main_catalog"

catalog_num_id="catalog_num"
main_catalog_num_id="main_catalog_num"


file_num_id="file_num"
file_name_id="file_name"
dest_path_id="dest_path"   
dir_name_id="dir_name"     
def classify_mp3_files(cur_dir):

    results=[{local_path_id:path} for path in mp3_files(cur_dir)]
    df=pd.DataFrame(results)
    df[name_id]=df[local_path_id].apply(ignore_pre_num_and_suffix)
    raw_catalog=df[name_id].apply(remove_suffix)
    raw_catalog=raw_catalog.apply(lambda x:x.split("-")).to_list()
    df[main_catalog_id]=[item[0] for item in raw_catalog]
    df[catalog_id]=[item[-1] for item in raw_catalog]
    
    catelog_num={}
    catalog_lst=unique(df[main_catalog_num_id].tolist())
    
    catalog_count=format_count(len(catalog_lst))
    
    
    for index,catalog in enumerate(catalog_lst):
        catelog_num[catalog]=f"{index:0{catalog_count}d}"

    df[main_catalog_num_id]=df[main_catalog_num_id].apply(lambda x:catelog_num[x])
    def _assign_in_numbers(group):
        results=group[name_id].tolist()
        count=format_count(len(results))
        catalog_num=group[catalog_num_id].iloc[0]
        dir_name=f"{catalog_num}_{group.name}"
        
        group[file_num_id]= [f"{index+1:0{count}d}" for index in range(len(results))]
        if dir_name_id in group.columns:
            group[dir_name_id]=f"{group[dir_name_id].iloc[0]}/ {dir_name}"
        else:
            group[file_num_id]= dir_name
        return group
        
    def _assign_numbers(group):
        results=unique(group[catalog_id].tolist())
        temp_count=len(results)
        
        if temp_count>1:
            catalog_num=group[main_catalog_num_id].iloc[0]
            dir_name=f"{catalog_num}_{group.name}"

            group[dir_name_id]=dir_name
            tem_dict={}
            for index, item in enumerate(results):
                tem_dict[item]=f"{index:0{format_count(temp_count)}d}"
            group[catalog_num_id]=group[catalog_id].apply(lambda x:tem_dict[x])
        else:
            df[catalog_num_id]=df[main_catalog_num_id]

        group.groupby(catalog_id, group_keys=False,sort=False).apply(_assign_in_numbers, include_groups=True)

        return group
    
    df=df.groupby(main_catalog_num_id, group_keys=False,sort=False).apply(_assign_numbers, include_groups=True)
    def assign_names(row):
        cur_path=Path(row["local_path"])
        file_name=f'{row[catalog_id]}_{row[file_num_id]}.mp3'

        dest_path=str(cur_path.parent/ row[dir_name_id] /file_name)
        return file_name,dest_path
    result =df.apply(assign_names,axis=1)
    df[file_name_id] = [x[0] for x in result]
    df[dest_path_id] = [x[1] for x in result]
    for index,row in df.iterrows():
        cur_path=Path(row["local_path"])
        file_name=f'{row[catalog_num_id]}_{row[file_num_id]}_{row[name_id]}.mp3'
        # row[file_name_id]=file_name
        # row[dest_path_id]=str(cur_path.parent/ row[dir_name_id] /file_name)
        
        
        # cur_path=row["local_path"]
        # dest_path=row["dest_path"]
        # move_file(cur_path,dest_path)
    
    
    
    df.to_excel(cur_dir+"\\mp3_files.xlsx",index=False)
    

    
    
if __name__=="__main__":
    
    # compile=re.compile(            r'第\d+讲\s*[（(]\s*第[一二三四五六七八九十0-9]+套\s*[）)]\s*')
    # val=compile.sub('',r"楞严经第272讲（第十二套 ) 观世音菩萨耳根圆通6")
    # print(val)
    # root_dir=r"E:\音乐\师兄u盘备份\华严经念诵2003"
    # move_mp3_files(root_dir,root_dir)
    
    root_dir=r"E:\音乐\师兄u盘备份\1慧律法师讲座mp3卡（32G)"
    classify_mp3_files(root_dir)