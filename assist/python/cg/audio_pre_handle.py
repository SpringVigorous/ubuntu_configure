from base import xlsx_files,df_empty,logger_helper,exception_decorator,recycle_bin,path_equal,get_df
from pathlib import Path
import os
import pandas as pd


def rename_imp(cur_path:str,root_name):
    
    old_path=r"E:\旭尧\有声读物"
    
    new_path=cur_path
    if root_name not in cur_path:
        new_path=cur_path.replace(old_path,f"{old_path}/{root_name}")
    
    return new_path

@exception_decorator(error_state=False)
def handle_catalog(xlsx_file,sheet_name):
    df=get_df(xlsx_file,sheet_name=sheet_name)
    if df_empty(df): 
        return
    cur_name=Path(df.iloc[0]["local_path"]).stem
    if "xlsx" in cur_name:
        return True
    df.dropna(subset=["href"],inplace=True)
    df["local_path"]=df["local_path"].apply(lambda x: rename_imp(x,"xlsx"))
    
    df.to_excel(xlsx_file,sheet_name=sheet_name,index=False)
    return True
@exception_decorator(error_state=False)
def handle_author(xlsx_file,sheet_name):
    df=get_df(xlsx_file,sheet_name=sheet_name)

    if df_empty(df): 
        df=get_df(xlsx_file,sheet_name="audio")
    if df_empty(df): 
        return
    def dest_func(file_path:str):
        
        if not file_path or not isinstance(file_path,str): 
            return file_path
        
        cur_path=Path(rename_imp(file_path,"xlsx"))
        if path_equal(cur_path,file_path): 
            return file_path
        
        
        
        dest= cur_path.parent.parent /cur_path.name
        return str(dest)
    
    
    df.dropna(subset=["href"],inplace=True)
    df["local_path"]=df["local_path"].apply(dest_func)
    df.to_excel(xlsx_file,sheet_name=sheet_name,index=False)
    return True
@exception_decorator(error_state=False)
def handle_album(xlsx_file,sheet_name):
    df=get_df(xlsx_file,sheet_name=sheet_name)

    if df_empty(df): 
        recycle_bin(xlsx_file)
        return
    df.dropna(subset=["href"],inplace=True)
    
    df["local_path"]=df["local_path"].apply(lambda x: rename_imp(x,"audio"))
    
    
    
    df.to_excel(xlsx_file,sheet_name=sheet_name,index=False)

    return True
def rename_sheet_name(xlsx_dir):
    
    
    logger=logger_helper(f"处理{xlsx_dir}")
    
    for xlsx_file in xlsx_files(xlsx_dir):
        
        logger.update_target(detail=f"当前文件：{xlsx_file}")
        cur_path=Path(xlsx_file)
        name=cur_path.stem
        if name =="catalog":
           result= handle_catalog(xlsx_file,sheet_name="catalog")
        elif "_album" not in name:
            result= handle_author(xlsx_file,sheet_name="album")
        else:
            result= handle_album(xlsx_file,sheet_name="audio")

        if not result: 
            logger.error("失败")
        else:
            logger.info("成功")
            


if __name__=="__main__":
    rename_sheet_name(r"E:\旭尧\有声读物\xlsx")
        
        