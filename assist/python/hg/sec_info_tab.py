
#sec_symbol_show.json信息整理的json文件
from dataclasses import replace
from itertools import count
from sys import meta_path
from matplotlib.pyplot import axis
import pandas as pd
import json
from os import path, system
import os



def read_json(filefullpath: str):
    data = None
    with open(filefullpath, "r", encoding='utf-8-sig') as f:
        data = json.loads(f.read())

    pf = pd.json_normalize(
        data, record_path=["cutMap", "cuts"], max_level=10, errors="ignore")

    pf.rename(columns={"start.refPt.XLocation.Distance": "st_x_val",
                             "start.refPt.XLocation.ReferenceAxis": "st_x_ref",
                             "start.refPt.YLocation.Distance": "st_y_val",
                             "start.refPt.YLocation.ReferenceAxis": "st_y_ref",
                             "end.refPt.XLocation.Distance": "ed_x_val",
                             "end.refPt.XLocation.ReferenceAxis": "ed_x_ref",
                             "end.refPt.YLocation.Distance": "ed_y_val",
                             "end.refPt.YLocation.ReferenceAxis": "ed_y_ref",
                             "start.orgPt.x": "st_org_x",
                             "start.orgPt.y": "st_org_y",
                             "end.orgPt.x": "ed_org_x",
                             "end.orgPt.y": "ed_org_y"
                             }, inplace=True)

    #转换为字符串

    pf[["st_x_val", "st_y_val", "ed_x_val", "ed_y_val"]] = pf[[
        "st_x_val", "st_y_val", "ed_x_val", "ed_y_val"]].astype(str)
    #合并列
    
    pf["st_ref"] = pf[["st_x_ref", "st_x_val"]].agg("#".join, axis=1)+"," + pf[["st_y_ref", "st_y_val"]].agg("#".join, axis=1)
    pf["ed_ref"]= pf[["ed_x_ref", "ed_x_val"]].agg("#".join, axis=1)+"," + pf[["ed_y_ref", "ed_y_val"]].agg("#".join, axis=1)
    pf["st_org"]=pf["st_org_x"].astype(str)+","+ pf["st_org_y"].astype(str)
    pf["ed_org"]=pf["ed_org_x"].astype(str)+","+ pf["ed_org_y"].astype(str)

    # 去除
    pf.drop(["st_x_val", "st_x_ref", "st_y_val", "st_y_ref", "ed_x_val",
                "ed_x_ref", "ed_y_val", "ed_y_ref","st_org_x","ed_org_x","st_org_y","ed_org_y"], inplace=True, axis=1, errors="ignore")
    
    #排序
    pf.sort_values(by=["blockId","name"],ascending=[True,True],inplace=True)

    # 输出到excel文档
    (filePath, __) = path.splitext(filefullpath)
    outPath = f"{filePath}-tab.xlsx"
    with pd.ExcelWriter(outPath) as writer:
        pf.to_excel(writer, sheet_name="location")

    system(outPath)


read_json(r"D:/客户端/sec_symbol_show.json")
