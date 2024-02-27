from dataclasses import replace
from itertools import count
from sys import meta_path
from matplotlib.pyplot import axis
import pandas as pd
import json
from os import path, system
import os
from sqlalchemy import false, true


def read_json(filefullpath1:str,filefullpath2:str,filefullpath3:str,curType:str):
    with open(filefullpath1,"rb") as f:
        data1=json.loads(f.read())

    with open(filefullpath2,"rb") as f2:
        data2=json.loads(f2.read())

    with open(filefullpath3,"rb") as f3:
        data3=json.loads(f3.read())


    # locationItem=pd.json_normalize(data1, max_level=10,errors="ignore")[['Floor','IDCode','Line','LineCmd','Level','Location','SectionName','eleType','sectionID']]
    # locationItem=pd.json_normalize(data1, max_level=10,errors="ignore")[['Floor','IDCode','Level','Location','SectionName','eleType','sectionID']]
    locationItem=pd.json_normalize(data1, max_level=10,errors="ignore")
    locationItem.drop(["Degree","EleType","FloorType","IncludeElement","Material","NearestAxis","ProtectThick","ReferenceProfile"],axis=1,inplace=True,errors="ignore")
    # f=lambda x:x.replace(r"\n","")
    if "Line" in locationItem.columns:
        locationItem["Line"]=locationItem["Line"].apply(lambda x: "".join(x))


    sectionItem=pd.json_normalize(data2, max_level=10,errors="ignore")
    sectionItem.drop(["reBar"],axis=1,inplace=True,errors="ignore")
    
    handleItem=pd.json_normalize(data3, max_level=10,errors="ignore")[[curType,"Floor"]]
    handleItem_floor=[]
    for i in  range(handleItem.shape[0]):
        curItem=pd.json_normalize(handleItem[curType].loc[i], max_level=10,errors="ignore")
        curItem.drop(["HandleInfo","Degree","UnitName"],axis=1,inplace=True,errors="ignore")
        curItem["Floor"]=handleItem["Floor"].loc[i]

        handleItem_floor.append(curItem)
    handle_Items_floor=pd.concat(handleItem_floor)

    loc_sec=pd.merge(locationItem,sectionItem,on="sectionID",how="outer")
    loc_handle=pd.merge(locationItem,handle_Items_floor,on="IDCode",how="outer")
    loc_sec_handle=pd.merge(loc_sec,loc_handle,on="IDCode",how="inner")

    # 输出到excel文档
    (filePath,__)=path.splitext(filefullpath1)
    outPath=f"{filePath}-{curType}-tab.xlsx"
    with pd.ExcelWriter(outPath) as writer:
        # locationItem.to_excel(writer,sheet_name="location")
        # sectionItem.to_excel(writer,sheet_name="section")
        
        #带楼层信息
        handle_Items_floor.to_excel(writer,sheet_name=f"handle_{curType}")
        loc_sec.to_excel(writer,sheet_name="location-section")
        loc_handle.to_excel(writer,sheet_name="location-handleMap")
        loc_sec_handle.to_excel(writer,sheet_name="location-section-handleMap")



    system(outPath)
    
filepath=r"E:\BIM\baijiayun\dispatch\drawing_recogniton_dispatch\cache_data\result_data_cache\20221217\1142\integration_result"
pre_name="PlatformWall"
curType="Wall"

read_json(f"{filepath}\{pre_name}Location.json",
          f"{filepath}\{pre_name}Section.json",
          f"{filepath}\HandleMap.json",
          curType
          )

