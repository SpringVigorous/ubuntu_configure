from sys import meta_path, prefix
import pandas as pd
import datacompy
import json
from os import path, system
from CompareConfig import CacachDir

def read_json(jsonPath:str):
    with open(jsonPath,"rb") as f:
        preData=json.loads(f.read())
    dwgfile=pd.json_normalize(preData,record_path=["DwgFiles"])
    Draw=pd.json_normalize(preData,record_path=["Drawings"])
    Block=pd.json_normalize(preData,record_path=["Blocks"])
    return (dwgfile,Draw,Block)



def read_DrawCmp(prePath:str,newPath:str):
    with open(prePath,"rb") as f:
        preData=json.loads(f.read())
    (preFile,preDraw,preBlock)=read_json(prePath)
    (newFile,newDraw,newBlock)=read_json(newPath)
    

   
    cmpFile = datacompy.Compare(preFile, newFile,join_columns="Guid")
    cmpDraw = datacompy.Compare(preDraw, newDraw,join_columns="Guid")
    cmpBlock = datacompy.Compare(preBlock, newBlock,join_columns="Guid")

    print("cmpFile")
    print(cmpFile.matches())
    print(cmpFile.report())
    print("-"*10)
    #
    print("cmpDraw")
    print(cmpDraw.matches())
    print(cmpDraw.report())
    print("-"*10)
    #
    print("cmpBlock")
    print(cmpBlock.matches())
    print(cmpBlock.report())
    print("-"*10)
    #


    # 输出到excel文档
    (filePath,__)=path.splitext(prePath)
    outPath=f"{filePath}-pre_new.xlsx"
    with pd.ExcelWriter(outPath) as writer:
        preFile.to_excel(writer,sheet_name="pre_Drawings")
        preDraw.to_excel(writer,sheet_name="pre_SubBlocks")
        preBlock.to_excel(writer,sheet_name="pre_Entitys")
        
        newFile.to_excel(writer,sheet_name="new_Drawings")
        newDraw.to_excel(writer,sheet_name="new_SubBlocks")
        newBlock.to_excel(writer,sheet_name="new_Entitys")
        
        writer.save()
        # writer.close()

    system(outPath)


preName="preModel.json"
newName="curModel.json"
prePath=f"{CacachDir}{preName}"
newPath=r"E:\BIM\baijiayun\dispatch\drawing_recogniton_dispatch\cache_data\result_data_cache\20221213\1119\Drawing.json"
# newPath=f"{CacachDir}{newName}"

read_DrawCmp(prePath,newPath)



