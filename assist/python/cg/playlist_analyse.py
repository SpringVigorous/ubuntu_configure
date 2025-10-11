

import os



from pathlib import Path



import re
import json
import sys
import asyncio
import re




from   base  import find_all,json_files,m3u8_files,df_empty,mp4_files,recycle_bin
root_path=r"F:\worm_practice/player/"
reg=re.compile(r"(.*?)-([a-f0-9]+)(?:-lost)?\.")

import pandas as pd

def split_names(file_path:str):
    cur_path=Path(file_path)
    
    file_name=cur_path.name
    
    match=reg.search(file_name)
    if not match:
        return None
    return {f"{cur_path.suffix[1:]}_path":file_path,"name":  match.group(1),"hash":match.group(2)}

def file_infos(sub_dir,func):
    m3u8_dir=os.path.join(root_path,sub_dir)
    lst=[]
    for file_name in func(m3u8_dir):
        names=split_names(file_name)
        if not names:
            continue
        lst.append(names)
    
    return pd.DataFrame(lst) if lst else None

def del_lost_files(df:pd.DataFrame,col_name:str):
    for index,row in df.iterrows():
        file_path=row[col_name]
        if file_path:
            recycle_bin(file_path)


if __name__=="__main__":
    m3u8_df=file_infos("m3u8",m3u8_files)
    url_df=file_infos("urls",json_files)
    mp4_lst=mp4_files(os.path.join(root_path,"video"))
    db_lst=mp4_files(r"F:\数据库")
    if db_lst:
        mp4_lst.extend(db_lst)
    mp4_df=pd.DataFrame(mp4_lst,columns=["mp4_path"])
    mp4_df["name"]=mp4_df["mp4_path"].apply(lambda x:Path(x).stem)

    
    m3u8_df=pd.merge(m3u8_df,mp4_df,on="name",how="outer")
    url_df=pd.merge(url_df,mp4_df,on="name",how="outer")
    
    lost_m3u8_df=m3u8_df[m3u8_df["mp4_path"].isnull()]
    lost_url_df=url_df[url_df["mp4_path"].isnull()]
    
    
    for index,row in lost_m3u8_df.iterrows():
        if row["m3u8_path"]:
            recycle_bin(row["m3u8_path"])

    del_lost_files(lost_m3u8_df,"m3u8_path")
    del_lost_files(lost_url_df,"json_path")
    
    
    
    
    
    
    
    