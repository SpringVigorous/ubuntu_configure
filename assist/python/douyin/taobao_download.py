import requests
import sys

from pathlib import Path
import os

root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )

from base import logger_helper,arabic_numbers
import pandas as pd
from taobao_config import *
from taobao_shop import read_xlsx_df


def id_name_dict()->dict:
    df=read_xlsx_df()
    if df is  None:
        return
    # 删除 goods_name 为空（NaN、''、' '）的行
    mask = (
        df['goods_name'].notna() &            # 过滤 NaN
        (df['goods_name'].str.strip() != '')   # 过滤空字符串或纯空格
    )
    df = df[mask]
    df["name"]=df.apply(lambda x: f'{x["shop_name"]}_{x["goods_name"]}',axis=1)
    dest_df=df[["name","itemId"]]
    # result=dest_df.to_dict(orient='records')
    result=dest_df.set_index("itemId")["name"].to_dict()

    return result
if __name__=="__main__":
    id_name_dict()





