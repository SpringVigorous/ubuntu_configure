from dataclasses import replace
from itertools import count
from sys import meta_path
from matplotlib.pyplot import axis
import pandas as pd
import json
from os import path, system
import os
from sqlalchemy import false, true


def read_json(filefullpath:str):
    with open(filefullpath,"rb") as f:
        data=json.loads(f.read())
    indata=data["missNameColumns"]
    preItem1=pd.json_normalize(indata,record_path=["ptr_wrapper","data","vLines_"],meta=[["ptr_wrapper","id"]], max_level=10,errors="ignore")
    preItem2=pd.json_normalize(indata,record_path=["ptr_wrapper","data","hLines_"],meta=[["ptr_wrapper","id"]],max_level=10,errors="ignore")
    preItem1["type"]="vLine"
    preItem2["type"]="hLine"

    # ids=preItem1[["ptr_wrapper.id"]]

    # preItem3=preItem1.append(preItem2)
    preItem3=pd.concat([preItem1,preItem2],axis=0)
    preItem3.sort_values(by='ptr_wrapper.id',inplace=True)      
    # preItem3.sort_values(by=['ptr_wrapper.id','s.entity.ptr_wrapper.data.handleVector_'],axis=1,inplace=True)      
    # group1=preItem3.groupby("ptr_wrapper.id")

    # preItem1=pd.json_normalize(data,record_path=["ptr_wrapper","data","vLines_"], max_level=10,errors="ignore")
    # preItem2=pd.json_normalize(data,record_path=["ptr_wrapper","data","hLines_"],max_level=10,errors="ignore")
    
    # 输出到excel文档
    (filePath,__)=path.splitext(filefullpath)
    outPath=f"{filePath}-tab.xlsx"
    with pd.ExcelWriter(outPath) as writer:
        preItem1.to_excel(writer,sheet_name="vLines_")
        preItem2.to_excel(writer,sheet_name="hLines_")
        preItem3.to_excel(writer,sheet_name="Lines_")
        # ids.to_excel(writer,sheet_name="all")


    system(outPath)
    
read_json(r"D:\项目资料\冯庄路车站\冯庄站台板分批后图纸\missNameColumns.json")


