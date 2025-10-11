import requests
import sys

from pathlib import Path
import os





from base import (
    logger_helper,
    UpdateTimeType,
    arabic_numbers,
    priority_read_json,
    xml_tools,
    concat_dfs,
    unique_df,
    download_sync,
    ThreadPool,
    merge_df,
    update_col_nums,
    assign_col_numbers,
    OCRProcessor,
    fix_url,
    concat_unique,
    get_param_from_url,
    write_to_json,
    except_stack,
    
)
import pandas as pd
from taobao_config import *
import requests
import glob
from bs4 import BeautifulSoup
import re
import random
import time 


product_column_names=set(["image",
item_id,
shop_id,
"title",
"itemUrl",
"vagueSold365",
])

dest_file_patern=re.compile(r'^(\d+).*$',re.DOTALL)
def dest_file_path(dir_name:str,file_name:str):
    org_name=Path(file_name).stem
    match= dest_file_patern.search(org_name)
    dest_dir=dir_name
    if match:
        sub_dir_name=match.group(1)
        dest_dir=os.path.join(dir_name,sub_dir_name)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir, exist_ok=True)
        

    return os.path.join(dest_dir,file_name)



def get_product_name_from_title(title:str)->str:
    """
    从文本中提取第一个中文中括号【】之间的内容
    :param text: 输入文本（字符串）
    :return: 第一个中括号内的内容（若无匹配则返回None）
    """
    quote_pattern = r'【(.*?)】'  # 匹配中文中括号并捕获中间内容
    match = re.search(quote_pattern, title)
    if match:
        return match.group(1)
    
    title = re.sub(r'阿四出品|木槿茶坊', '', title)
    title = re.sub(r'^\s*\|+\s*', '', title)
    
    # 正则表达式：匹配从开头到第一个空格或标点的部分
    split_pattern = r'[^\s，。！？、；：“”‘’—《》….,!?;:\'"\-]+'
    secs = re.findall(split_pattern, title)
    
    # 正则表达式：匹配从开头到第一个关键词的文本
    flag_pattern = r'^.*?[茶粉干块糕水汤仁粥羹膏]'
    
    for sec in secs:
        match = re.search(flag_pattern, sec)
        if match:
            return match.group(0)
        
    return 
        
    
    


    
#店铺首页url
def shop_home_url(user_id:str|int):
    return f"https://shop.m.taobao.com/shop/shop_index.htm?user_id={user_id}"

def user_id_by_shop_home_url(url:str)->str:
    return get_param_from_url(url,"user_id")



#店铺产品url
def shop_goods_url(shop_id:str|int):
    return f"https://shop{shop_id}.taobao.com/?spm=tbpc.mytb_followshop.item.shop"

def shop_id_by_shop_goods_url(url:str)->str:
    # pattern = r"shop(\d+)"
    pattern = r"//shop(\d+)\.taobao\.com"
    results= re.findall(pattern, url)
    if results:
        return results[0]
    return None


def bracket_params_to_dict(org_str:str,prefix_str:str)->str:
    # 正则匹配
    
    pattern=prefix_str+r'[\d]*\((.*?)\)$'
    
    reg = re.compile(pattern, re.DOTALL)
    matches = reg.findall(org_str)

    if matches:
        json_str = matches[0].strip()
        try:
            data = json.loads(json_str)
            return data
        except json.JSONDecodeError:
            print("JSON格式错误")
    
    return None

def org_shop_to_df(data:dict):
    df=pd.DataFrame(data)
    return df
    
#店铺名，主页，用户名
def org_shop_dict_from_product(org_data:dict)->dict:
    if not org_data or "data" not in org_data:
        return 
    #店铺id
    shopId=org_data.get(shop_id,None)
    
    data=org_data["data"]
    if  "signInfoDTO" not in data:
        return
    shop_data=data["signInfoDTO"]
    
    name=shop_data.get("shopName",None)
    home_url=shop_data.get("shopUrl",None)
    userId=get_param_from_url(home_url,"user_id")
   
    result={shop_name_id:name,home_url_id:home_url,user_id:userId,shop_id:shopId}
    return result
def org_product(org_data:dict)->list[dict]:
    if not org_data or "data" not in org_data:
        return 
    #店铺id
    shopId=org_data.get(shop_id,None)

    data=org_data["data"]
    
    if "itemInfoDTO" in data:
        data=data["itemInfoDTO"]
    if "data" in data:
        data=data["data"]
    
    for item in data:
        item[shop_id]=shopId
    
    # print(data)
    return data

def org_procduct_to_df(org_data:dict):
    data=org_product(org_data)
    if not data:
        return pd.DataFrame()
    df=pd.DataFrame(data)
    column_names=df.columns.tolist()
    
    # print(column_names)
    
    remove_names=set(column_names).difference(product_column_names)
    df.drop(columns=remove_names,inplace=True)
    df[item_id]=df[item_id].astype(str)
    if 'vagueSold365' in df.columns:
        df["sold"]=df["vagueSold365"].apply(lambda x:arabic_numbers(x)[0])
    else:
        df["sold"]=-1
        
    df["goods_name"]=None
    df[num_id]=-1
    
    # print(df)
    
    return df

def product_df_from_json(shop_name:str)->pd.DataFrame:
    
    dfs=[]
    
    for file in glob.glob(f"{shop_dir}/*{shop_name}*.json"):
        data=priority_read_json(file,encoding="utf-8-sig")
        if not data:
            continue
        data_df=org_procduct_to_df(data)
        if data_df is None:
            continue
        data_df["shop_name"]=shop_name
        dfs.append(data_df) 
    
    
    return pd.concat(dfs)
def arrage_product_df(df:pd.DataFrame):
   
    df.sort_values(by=["sold","goods_name"],ascending=[False,False],inplace=True)
    df.drop_duplicates(subset=[item_id],inplace=True,ignore_index=True)
    df.sort_values(by=["sold"],ascending=False,inplace=True)
    
    df=assign_col_numbers(df,num_id)
    # print(df)

    return df

def org_main_lst(org_data:dict)->list:
    if not org_data or "data" not in org_data:
        return 

    data=org_data["data"]
    item=data["item"]
    pic_url=item["images"]
    id=item[item_id]
    urls=[fix_url(url) for url in pic_url]

    return [{item_id:id,pic_url_id:url,type_id:0,num_id:-1,pic_name_id:""} for url in urls]
def json_main_df():
    results=[]
    
    for file in glob.glob(f"{main_dir}/*.json"):
        data=priority_read_json(file,encoding="utf-8-sig")
        if not data:
            continue
        results.extend(org_main_lst(data))

    return pd.DataFrame(results)
    
import json
def org_desc_lst(json_data:dict,userid:str=None)->list[dict]:
    result=[]
    if not json_data:
        return result
    itemId=json_data.get(item_id)
    
    data=json_data.get("data",None)
    if not data:
        return result
    data=data.get("components",None)
    if not data:
        return result
    layout_data:list=data.get("layout")

    pic_dict:dict=data.get("componentData")
    

    # pic_lst=[{"ID":id,"data":json.dumps(item)} for id,item in pic_dict.items()]
    # lay_df=pd.DataFrame(layout_data)
    # pic_df=pd.DataFrame(pic_lst)
    # print(lay_df)
    # print(pic_df)
    
    # df=pd.merge(lay_df,pic_df,on="ID",how="outer",sort=False)
    # df.to_excel("layout.xlsx")
    
    
    for item in layout_data:
        id=item.get("ID",None)
        if not id or id not in pic_dict:
            continue
        
        
        dest=pic_dict[id]
        
        
        #其他产品的链接
        children=dest.get("children",None)
        
        #店铺其他产品链接
        if children:
            continue
        
        model=dest.get("model",None)
        if not model:
            continue
        picUrl=model.get("picUrl",None)
        if not picUrl:
            continue
        url=fix_url(picUrl)
        if userid  and userid not in url:
            #制式图片，
            continue
        
        result_item={item_id:itemId,pic_url_id:url,type_id:1,num_id:-1} 
        
        
        result.append(result_item )

        
        
    
    return result
    





def org_desc_dict_lst(html_content,id)->list:
    if not html_content :
        return 
    # 解析 HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # 找到所有 <div class="descV8-singleImage"> 下的 <img> 标签
    img_tags = soup.select('div.descV8-container div.descV8-singleImage img')

    # 提取 src 属性
    img_srcs = [img['data-src'] if   'data-src' in img.attrs else img["src"] for img in img_tags if 'src' in img.attrs or 'data-src' in img.attrs]
    return [{item_id:id,pic_url_id:url,type_id:1,num_id:-1,pic_name_id:""} for url in img_srcs]

def xml_desc_df():
    results=[]
    for file in glob.glob(f"{desc_dir}/*.html"):
        with open(file, 'r', encoding='utf-8-sig') as f:
            html_content=f.read()
            item_id=os.path.basename(file).split(".")[0]
            results.extend(org_desc_dict_lst(html_content,item_id))
    return pd.DataFrame(results)



def id_name_dict(df:pd.DataFrame)->dict:

    if df is  None or df.empty:
        return
    # # 删除 goods_name 为空（NaN、''、' '）的行
    # mask = (
    #     df['goods_name'].notna() &            # 过滤 NaN
    #     (df['goods_name'].str.strip() != '')   # 过滤空字符串或纯空格
    # )
    # df = df[mask].copy()
    
    #需要测试下
    result=df.set_index(item_id)[num_id].apply(lambda x:f"{x:03}").to_dict()

    return result






def arrage_product(df:pd.DataFrame,id):
    df.sort_values(by=["sold","goods_name"],ascending=[False,False],inplace=True)
    df.drop_duplicates(subset=[item_id],inplace=True,ignore_index=True)
    df.sort_values(by=["sold"],ascending=False,inplace=True)
    
    df=assign_col_numbers(df,num_id)
    # print(df)

    return df


def get_pic_name(product_num:int,type:int,index:int,fix_count:int=3)->str:
    return f"{product_num:0{fix_count}}_{type}_{index:03}"


def arrange_pic(df:pd.DataFrame,id_dict:dict,fix_num:int=3):
    df=update_col_nums(df,[item_id,type_id],num_id)
    # df[name_id]=df.apply(lambda x:f"{id_dict.get(x[item_id]):0{good_num}}_{x['type']}_{int(x[num_id]):03}",axis=1)
    df[name_id]=df.apply(lambda x:get_pic_name(id_dict.get(x[item_id],-1),int(x['type']),int(x[num_id]),fix_num),axis=1)
    return df





def download_pics(df:pd.DataFrame,cache_thread:ThreadPool,ocr_lst,headers):
    # cache_thread._start()
    logger=logger_helper("下载图片")
    def _download(url,dest_path):
        
        logger.update_target(detail=f"{url}->{dest_path}")
        
        def ocr_text(org_path,ocr_path):
            
            logger=logger_helper("文字识别",f"{dest_path}->{ocr_path}")
            ocr_pic=OCRProcessor()
            _,texts=ocr_pic.process_image(org_path,output_path=ocr_path)
            
            ocr_lst.append({"name":Path(org_path).stem,"text":";".join(texts) if texts else ""})
            pass
        

        try:
            if download_sync(url,dest_path,headers=headers):
                
                ocr_path= dest_file_path(ocr_pic_dir, Path(dest_path).name)
                if os.path.exists(ocr_path):
                    return

 
                cache_thread.submit(ocr_text,dest_path,ocr_path)
                pass
        except  Exception as e:
            logger.error("异常",f"原因：{e}",update_time_type=UpdateTimeType.STAGE)
        
    
    for index,row in df.iterrows():
        url=row[pic_url_id]
        if not url:
            continue
        name=row[name_id]
        if not url or not name:
            continue
        file_path=dest_file_path(org_pic_dir,f"{name}.jpg")
        cache_thread.submit(_download,url,file_path)
    

#从主图信息中提取sku信息
def sku_infos_from_main(json_data: dict) -> list:
    """
    从 JSON 数据中安全提取 image 和 name 字段
    :param json_data: 输入的 JSON 字典
    :return: 包含有效数据的 DataFrame
    """
    if not json_data:
        return
    data=json_data.get("data", {})
    if not data:
        return
    itemId=json_data[item_id]
    
    extracted_data = []
    
    # 安全层级检查
    sku_base = data.get("skuBase", {})
    props = sku_base.get("props", [])
    
    for prop in props:
        # 检查 values 是否存在且为列表
        values = prop.get("values", [])
        if not isinstance(values, list):
            continue
            
        for value in values:
            # 安全提取字段
            image = value.get("image", "")
            name = value.get("name", "")
            
            # 输入过滤：跳过空值
            if not image or not name:
                continue
            
            extracted_data.append({
                item_id:itemId,
                pic_url_id: image,
                pic_name_id: name.strip(),  # 去除前后空格
                type_id:3,
                num_id:-1,
            })
    
    return extracted_data