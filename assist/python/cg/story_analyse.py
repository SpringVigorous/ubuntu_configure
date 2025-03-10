import os
import sys

from pathlib import Path

import pandas as pd
import numpy as np


root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )

from base import (
    find_all
)

base_pattern= r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*?第(\d+)个_(.*?)】-.*?【BASE】详情：(.*?),'
def get_pattern(flag):
    return base_pattern.replace("BASE",flag)

def handle_df(df):
    df["num"]=df["num"].astype(int)
    df["time"]=pd.to_datetime(df["time"])
    df.drop_duplicates(subset=["url","num","title"],keep="last",inplace=True)
    return df



if __name__=="__main__":
    start_pattern =get_pattern("开始")
    end_pattern = get_pattern("完成")
    args=["time","num","title","url"]
    
    log_content=''
    with open(r"\\Springflourish\f\worm_practice\logs\story_wrapper\story_wrapper-trace.log","r",encoding="utf-8-sig") as f:
        log_content=f.read()
    if not log_content:
        exit(0)

    
    beg_df=handle_df(pd.DataFrame(find_all(log_content,start_pattern,args)))
    end_df=handle_df(pd.DataFrame(find_all(log_content,end_pattern,args)))
    merge_df=beg_df.merge(end_df,how="outer",on=["url","num","title"],suffixes=("_beg","_end"))
    merge_df["valid"]=np.where(merge_df["time_end"]>merge_df["time_beg"],1,0)

    merge_df=merge_df.sort_values(by="num",ascending=True).reset_index(drop=True)
    merge_df.to_excel("story_wrapper.xlsx")