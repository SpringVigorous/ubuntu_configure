from sys import meta_path
import pandas as pd
import json
from os import path, system,walk,listdir




def read_json(filefullpath:str):
    item=None
    try:
        with open(filefullpath,"rb") as f:
            data=json.loads(f.read())
        item=pd.json_normalize(data, max_level=10,errors="ignore")
        item.drop(['Handles'],axis=1,inplace=True,errors="ignore")
    finally:
        return item

def export_data(dirPath:str):
    datas=[]
    for file in listdir(dirPath):
        filePath=path.join(dirPath,file)
        if path.isfile(filePath) and path.splitext(filePath)[1]==".json":
            data=read_json(filePath)
            if data is not None:
                datas.append(data)
    
    result=pd.concat(datas)
    outPath=path.join(dirPath,"blocks_tab.xlsx")
    with pd.ExcelWriter(outPath) as writer:
        result.to_excel(writer,sheet_name="blocks")
    system(outPath)

filePath=r"E:\BIM\baijiayun\dispatch\drawing_recogniton_dispatch\cache_data\mid_data_cache\20221214\1137\mid_result\split_block"
export_data(filePath)