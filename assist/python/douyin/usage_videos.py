import os
import re

from pathlib import Path
import sys
root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )
from dy_unity import OrgInfo,DestInfo,dy_root
from base import  logger_helper,UpdateTimeType,download_sync,read_content_by_encode,unique,columns_index
from base import copy_file,fill_adjacent_rows,merge_df,sparse_columns_name,merge_all_identical_column_file
import json
import pandas as pd
from split_mp4 import SplitBase

class HandleUsage:
    
    def __init__(self) -> None:
        
        spliter=SplitBase()
        pass
    @staticmethod
    def _load_usage_json(file_name):
        with open(dy_root.usage_src_path(file_name), 'r', encoding='utf-8') as file:
            return json.load(file)
    @staticmethod
    def _save_usage_json(file_name, data):
        with open(dy_root.usage_src_path(file_name), 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    @staticmethod
    def load_usage_json():
        with open(dy_root.usage_src_path(HandleUsage.usage_json_name()), 'r', encoding='utf-8') as file:
            return json.load(file)
    @staticmethod
    def save_usage_json(data):
        with open(dy_root.usage_src_path(HandleUsage.usage_json_name()), 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)


    @staticmethod
    #根据筛选的路径拷贝到一个目录中,用之前先调用save_usage
    def copy_by_json(json_name:str=None):
        if not json_name:
            json_name=HandleUsage.usage_json_name()
        data=HandleUsage._load_usage_json(json_name)
        results={}
        for item in data:
            name=item["name"]
            files= unique(item["videos"])
            
            if name  in results:
                results[name].extend(files)
            else:
                results[name]=files
            
        for name,files in results.items():
            copy_file(files,dy_root.usage_sub_dir(name),override=False)
        pass    
    pass


    @staticmethod
    #根据筛选的路径拷贝到一个目录中,用之前先调用save_usage
    def copy_by_txt(txt,name):
        if not txt or not name:
            return
        

        
        
        lst=[os.path.join(dy_root.dest_sub_dir(DestInfo(file).series_name),file)  for file in txt.split()]
        if not lst:
            return
        results={name:lst}
        for name,files in results.items():
            copy_file(files,dy_root.usage_sub_dir(name),override=False)


        data=HandleUsage.load_usage_json()
        keys=[item["name"] for item in data]
        if name in keys:
            data[keys.index(name)]["videos"]=lst
        else:
            data.append({"name":name,"videos":lst})
        HandleUsage.save_usage_json(data)

            #输出保存
        HandleUsage.save_usage_xlsx(pd.DataFrame(data))
        
    pass


    @staticmethod
    def save_usage_xlsx(df:pd.DataFrame):
        _,columns=sparse_columns_name(df)
        xls_path,sheet_name=dy_root.usage_info_xlsx_path
        
        df.to_excel(xls_path, sheet_name=sheet_name, index=False)
        front_index=[index+1 for index in columns_index(df,columns)]
        
        
        
        merge_all_identical_column_file(xls_path,sheet_name=sheet_name,col_index=front_index)

    @staticmethod
    def load_usage_xlsx():
        xls_path,sheet_name=dy_root.usage_info_xlsx_path
        df=pd.read_excel(xls_path,sheet_name=sheet_name)
        df=fill_adjacent_rows(df,['原始文件'])
        
        
        sparse_names,columns=sparse_columns_name(df)
        num_lst=list(filter(lambda x: not isinstance(x,str),sparse_names))
        if num_lst:
            df.rename(columns={item:str(item) for item in num_lst},inplace=True)
        
        
        df=fill_adjacent_rows(df,columns)
        return df
        
        
    @staticmethod
    def init_usage_xlsx():
        df=SplitBase().load_split_xlsx()
        df.drop(columns=["分辨率","总时长"],inplace=True)#删除无用列
        df=fill_adjacent_rows(df)
        HandleUsage.save_usage_xlsx(df)
            
    
    #用户在 视频使用信息中填充的信息，会保存到json文件中
    @staticmethod
    def save_usage(json_name:str=None):
        df=HandleUsage.load_usage_xlsx()
        columns,_=sparse_columns_name(df)
        results=[]
        for column in columns:
            # 假设你的 DataFrame 名称是 df
            condition = (df[column].notna()) & (df[column] == 1)  # 筛选条件
            result_list = df.loc[condition, '文件名'].tolist()    # 提取 G 列并转为列表
            data=[os.path.join(dy_root.dest_sub_dir(DestInfo(name).series_name),name)  for name in result_list]
            results.append({"name":str(column),"videos":data})
        if not json_name:
            json_name=HandleUsage.usage_json_name()
        HandleUsage._save_usage_json(f"{json_name}",results)

        
        
    @staticmethod
    def load_usage_by_json(json_name:str=None):
        
        if not json_name:
            json_name=HandleUsage.usage_json_name()
        
        df=None
        data=HandleUsage._load_usage_json(json_name)

        for item in data:
            result=[]
            column=Path(item["name"]).name
            for file in item["videos"]:
                file=Path(file).name
                result.append({"文件名":file,column:1})
            cur_df=pd.DataFrame(result)
            if df is None:
                df=cur_df
            else:
                df=merge_df(cur_df,df,on="文件名",how="outer")
        return df
    @staticmethod
    def merge_usage(json_df:pd.DataFrame):
        org_df=HandleUsage.load_usage_xlsx()
        df=merge_df(org_df,json_df,on="文件名",how="left",keep_first=False)
        return df
            
            
    @staticmethod
    def usage_json_name():
        return "1"
            
           

def first_init():
    #第一次使用，基本上用不着
    HandleUsage.init_usage_xlsx() 
 
def show_usage_xlsx():    
    #json文件保存了之前的用户使用信息，先加载
    logger=logger_helper("加载用户使用信息","来自json文件")
    usage_df=HandleUsage.load_usage_by_json()
    #和xlsx数据合并
    usage_df=HandleUsage.merge_usage(usage_df)
    logger.info(f"完成,共{len(usage_df.index)-1}条")
    #输出保存
    HandleUsage.save_usage_xlsx(usage_df)
    HandleUsage.save_usage()
    

    
    
    
def main():
    #第一次使用，基本上用不着
    # first_init()

    #打开xlsx文件以及json文件，整合后 导出xlsx文件（单元格已合并），同时修改json文件
    show_usage_xlsx()
    
    #根据json文件中，拷贝对应的文件
    # HandleUsage.copy_by_json()
    
    txt="""
鼋头渚夜樱_005-1920x1080_003.mp4
鼋头渚夜樱_011-720x1280_002.mp4
鼋头渚夜樱_003-720x1560_007.mp4
鼋头渚夜樱_011-720x1280_003.mp4
鼋头渚夜樱_011-720x1280_004.mp4
鼋头渚夜樱_003-720x1560_006.mp4
    """
    
    HandleUsage.copy_by_txt(txt,"2")

if __name__=="__main__":
    main()