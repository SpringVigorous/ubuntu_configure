import requests
import sys

from pathlib import Path
import os

root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )

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
)
import pandas as pd
from taobao_config import *
import requests
import glob
from bs4 import BeautifulSoup
cookies = {
    't': 'fc0f8a4da755a465f79430716bfaed6a',
    'cna': 'ArEsIEQEnkgCAWVd/GueTwU3',
    'wk_cookie2': '107e7cda93a3127e076c5480ce338433',
    'wk_unb': 'W8nRNZ5h08yA',
    'lgc': '%5Cu6E05%5Cu98CE%5Cu7EC6%5Cu96E8spring',
    'dnk': '%5Cu6E05%5Cu98CE%5Cu7EC6%5Cu96E8spring',
    'tracknick': '%5Cu6E05%5Cu98CE%5Cu7EC6%5Cu96E8spring',
    'cookie2': '28c442dc6cf9f470289e5ed717c7cadb',
    '_tb_token_': 'ee45e3b86ef38',
    'thw': 'xx',
    'cancelledSubSites': 'empty',
    'havana_lgc2_0': 'eyJoaWQiOjgwNTM0NjIxMSwic2ciOiI4YjU3NTFmZjIzN2FlZThiZjRiYWRiNWJlMzg4NWZhYiIsInNpdGUiOjAsInRva2VuIjoiMXdCY25kVXRJclQwV01xcFA2TTliYXcifQ',
    '_hvn_lgc_': '0',
    'sn': '',
    'useNativeIM': 'false',
    'wwUserTip': 'false',
    'cnaui': '805346211',
    'aui': '805346211',
    'sca': 'b78d0b87',
    '_samesite_flag_': 'true',
    'sgcookie': 'E100IBiCbSLO4jwEkfQp0ONA1KRipcZZq0TLFt9JVCVTeculNMTWVlybRlk%2FHhOZq6m%2BCPpEoRSM9cP0OcMI4YnJ2ZxUAnUB%2FdiwnGEkEIhdh3YeUBxKRL%2FBg966KS9Dza0n',
    'havana_lgc_exp': '1777015183349',
    'unb': '805346211',
    'uc3': 'nk2=pIQhhU61mKqxd8G%2F%2Fec%3D&id2=W8nRNZ5h08yA&lg2=WqG3DMC9VAQiUQ%3D%3D&vt3=F8dD2ESoLrVHhm2%2FoOw%3D',
    'csg': '37aecf68',
    'cookie17': 'W8nRNZ5h08yA',
    'skt': 'a4bd6fa005c080f8',
    'existShop': 'MTc0NTkxMTE4Mw%3D%3D',
    'uc4': 'id4=0%40WepztFUfrjka2veu6LEVE699LXw%3D&nk4=0%40pkd7LVvh2nTowDrZXKDnKT2ahD8sQib%2FSQ%3D%3D',
    '_cc_': 'WqG3DMC9EA%3D%3D',
    '_l_g_': 'Ug%3D%3D',
    'sg': 'g1d',
    '_nk_': '%5Cu6E05%5Cu98CE%5Cu7EC6%5Cu96E8spring',
    'cookie1': 'V3%2FenGW6GG%2BLswAOlWyHD7%2FWwY7HTXh8PHuWlKn1po0%3D',
    'sdkSilent': '1745997583387',
    'havana_sdkSilent': '1745997583387',
    'xlly_s': '1',
    'uc1': 'cookie21=UtASsssmfaCOMId3WwGQmg%3D%3D&cookie15=Vq8l%2BKCLz3%2F65A%3D%3D&existShop=false&pas=0&cookie16=W5iHLLyFPlMGbLDwA%2BdvAGZqLg%3D%3D&cookie14=UoYajlzIM6cJSQ%3D%3D',
    'mtop_partitioned_detect': '1',
    '_m_h5_tk': 'dd65b695361273853c7d57d6cb70668d_1745937270900',
    '_m_h5_tk_enc': 'd69f64ae223dcdf636b121d11bd6efbb',
    'isg': 'BF9fYwPxSwZycEKJXvbUD9x37rPpxLNmF9AoEPGsKI4agH0C-5BZt6AWQhD-GIve',
    'tfstk': 'gG_xnJZLu820kZ_vZsrojFycPcPlDuf2yt5ISdvmfTBR1t9DIhiXFbO99c96h1O6WT6ggKf_3OQ9FEtNmdvDBFCNp723-yfVgF8QKJ4hfkGmUEOXCIT_1LO267AX3nKksF8_KJmo5nzp7t99UVTjVQ9y6Iis5OgSFC9WGmtfCLtWOBDX5O66PLOeTxMXfCtSFLR65C66c_NJsLOX5FGQmSprGI3OY4Z1v1qPCVg1yIK7qsvWcnFMgnh1MLu_dwRx8p1XeVgMpKE6D_C0H25kuZWptt4Sk9CFzTd5dPeJ7TS1CCB78AYVxt7e2tqIP_TvFH95RyMJag1cfZWx6VOVowx9L3Fs7hY5-HsCHfPFNEO1QH7gLqJf167FxeUoce1Rf9IO4R_hJ5UsKp_tc7F-bc-XavkkIt6DOiqywpVXccowjQRJK7dnbc-XaQp3MMiZbhAP.',
}

headers = {
    'authority': 'h5api.m.taobao.com',
    'accept': 'application/json',
    'accept-language': 'zh-CN,zh;q=0.9',
    'content-type': 'application/x-www-form-urlencoded',
    # Requests sorts cookies= alphabetically
    # 'cookie': 't=fc0f8a4da755a465f79430716bfaed6a; cna=ArEsIEQEnkgCAWVd/GueTwU3; wk_cookie2=107e7cda93a3127e076c5480ce338433; wk_unb=W8nRNZ5h08yA; lgc=%5Cu6E05%5Cu98CE%5Cu7EC6%5Cu96E8spring; dnk=%5Cu6E05%5Cu98CE%5Cu7EC6%5Cu96E8spring; tracknick=%5Cu6E05%5Cu98CE%5Cu7EC6%5Cu96E8spring; cookie2=28c442dc6cf9f470289e5ed717c7cadb; _tb_token_=ee45e3b86ef38; thw=xx; cancelledSubSites=empty; havana_lgc2_0=eyJoaWQiOjgwNTM0NjIxMSwic2ciOiI4YjU3NTFmZjIzN2FlZThiZjRiYWRiNWJlMzg4NWZhYiIsInNpdGUiOjAsInRva2VuIjoiMXdCY25kVXRJclQwV01xcFA2TTliYXcifQ; _hvn_lgc_=0; sn=; useNativeIM=false; wwUserTip=false; cnaui=805346211; aui=805346211; sca=b78d0b87; _samesite_flag_=true; sgcookie=E100IBiCbSLO4jwEkfQp0ONA1KRipcZZq0TLFt9JVCVTeculNMTWVlybRlk%2FHhOZq6m%2BCPpEoRSM9cP0OcMI4YnJ2ZxUAnUB%2FdiwnGEkEIhdh3YeUBxKRL%2FBg966KS9Dza0n; havana_lgc_exp=1777015183349; unb=805346211; uc3=nk2=pIQhhU61mKqxd8G%2F%2Fec%3D&id2=W8nRNZ5h08yA&lg2=WqG3DMC9VAQiUQ%3D%3D&vt3=F8dD2ESoLrVHhm2%2FoOw%3D; csg=37aecf68; cookie17=W8nRNZ5h08yA; skt=a4bd6fa005c080f8; existShop=MTc0NTkxMTE4Mw%3D%3D; uc4=id4=0%40WepztFUfrjka2veu6LEVE699LXw%3D&nk4=0%40pkd7LVvh2nTowDrZXKDnKT2ahD8sQib%2FSQ%3D%3D; _cc_=WqG3DMC9EA%3D%3D; _l_g_=Ug%3D%3D; sg=g1d; _nk_=%5Cu6E05%5Cu98CE%5Cu7EC6%5Cu96E8spring; cookie1=V3%2FenGW6GG%2BLswAOlWyHD7%2FWwY7HTXh8PHuWlKn1po0%3D; sdkSilent=1745997583387; havana_sdkSilent=1745997583387; xlly_s=1; uc1=cookie21=UtASsssmfaCOMId3WwGQmg%3D%3D&cookie15=Vq8l%2BKCLz3%2F65A%3D%3D&existShop=false&pas=0&cookie16=W5iHLLyFPlMGbLDwA%2BdvAGZqLg%3D%3D&cookie14=UoYajlzIM6cJSQ%3D%3D; mtop_partitioned_detect=1; _m_h5_tk=dd65b695361273853c7d57d6cb70668d_1745937270900; _m_h5_tk_enc=d69f64ae223dcdf636b121d11bd6efbb; isg=BF9fYwPxSwZycEKJXvbUD9x37rPpxLNmF9AoEPGsKI4agH0C-5BZt6AWQhD-GIve; tfstk=gG_xnJZLu820kZ_vZsrojFycPcPlDuf2yt5ISdvmfTBR1t9DIhiXFbO99c96h1O6WT6ggKf_3OQ9FEtNmdvDBFCNp723-yfVgF8QKJ4hfkGmUEOXCIT_1LO267AX3nKksF8_KJmo5nzp7t99UVTjVQ9y6Iis5OgSFC9WGmtfCLtWOBDX5O66PLOeTxMXfCtSFLR65C66c_NJsLOX5FGQmSprGI3OY4Z1v1qPCVg1yIK7qsvWcnFMgnh1MLu_dwRx8p1XeVgMpKE6D_C0H25kuZWptt4Sk9CFzTd5dPeJ7TS1CCB78AYVxt7e2tqIP_TvFH95RyMJag1cfZWx6VOVowx9L3Fs7hY5-HsCHfPFNEO1QH7gLqJf167FxeUoce1Rf9IO4R_hJ5UsKp_tc7F-bc-XavkkIt6DOiqywpVXccowjQRJK7dnbc-XaQp3MMiZbhAP.',
    'origin': 'https://shop293825603.taobao.com',
    'referer': 'https://shop293825603.taobao.com/?spm=pc_detail.29232929/evo365560b447259.shop_block.dshopinfo.74fc7dd6lK3g0k',
    'sec-ch-ua': '"Not)A;Brand";v="24", "Chromium";v="116"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.97 Safari/537.36 SE 2.X MetaSr 1.0',
}

params = {
    'jsv': '2.6.2',
    'appKey': '12574478',
    't': '1745932088118',
    'sign': '1b6a562b74406b3dad5929c9c7370c63',
    'api': 'mtop.taobao.shop.simple.item.fetch',
    'type': 'originaljson',
    'v': '1.0',
    'timeout': '10000',
    'dataType': 'json',
    'sessionOption': 'AutoLoginAndManualLogin',
    'needLogin': 'true',
    'LoginRequest': 'true',
    'jsonpIncPrefix': '_1745932088117_',
    'data': '{"page":2,"orderType":"popular","sortType":"","catId":0,"keyword":"","filterType":"","shopId":"293825603","sellerId":"2208692291653"}',
}

# response = requests.get('https://h5api.m.taobao.com/h5/mtop.taobao.shop.simple.item.fetch/1.0/', params=params, cookies=cookies, headers=headers)



def fetch_data():
    logger=logger_helper("获取店铺产品信息")
    try:
        response = requests.get('https://h5api.m.taobao.com/h5/mtop.taobao.shop.simple.fetch/1.0/', params=params, cookies=cookies, headers=headers)
        org_data=response.json()
        return org_data
    except Exception as e:
        logger.error("失败",f"失败原因：{e}")
        return None
    
    
column_names=set(["image",
item_id,
"title",
"itemUrl",
"vagueSold365"])


    
    
def org_shop_to_df(org_data:dict):
    if not org_data or "data" not in org_data:
        return 

    data=org_data["data"]
    
    shop_name="未知"
    if  "signInfoDTO" in data:
        shop_data=data["signInfoDTO"]
        shop_name=shop_data["shopName"]
    if "itemInfoDTO" in data:
        data=data["itemInfoDTO"]
    if "data" in data:
        data=data["data"]
        
    df=pd.DataFrame(data)
    remove_names=set(df.columns.tolist()).difference(column_names)
    df.drop(columns=remove_names,inplace=True)
    df[item_id]=df[item_id].astype(str)
    df["sold"]=df["vagueSold365"].apply(lambda x:arabic_numbers(x)[0])
    df["goods_name"]=None
    df["shop_name"]=shop_name
    df[num_id]=None
    return df

def json_shop_df(shop_name:str)->pd.DataFrame:
    
    dfs=[]
    
    for file in glob.glob(f"{shop_dir}/*{shop_name}*.json"):
        data=priority_read_json(file,encoding="utf-8-sig")
        if not data:
            continue
        data_df=org_shop_to_df(data)
        if data_df is None:
            continue
        data_df["shop_name"]=shop_name
        dfs.append(data_df) 
    
    
    return pd.concat(dfs)

def read_xlsx_df():
    shop_df,pic_df=[None]*2
    if os.path.exists(xlsx_file):
        with pd.ExcelFile(xlsx_file) as reader:
            sheetnames=reader.sheet_names
            def get_df(name:str)->pd.DataFrame:
                if name not in sheetnames:
                    return None
                df=reader.parse(name)
                if item_id in df.columns:
                    df[item_id]=df[item_id].astype(str)
                return df

            shop_df = get_df(shop_name)
            pic_df =  get_df(pic_name)
            ocr_df=get_df(orc_name)


    return shop_df,pic_df,ocr_df


def save_xlsx_df(data_df:pd.DataFrame,pic_df:pd.DataFrame,ocr_df:pd.DataFrame):
    
    with pd.ExcelWriter(xlsx_file,mode="w") as w:
        data_df.to_excel(w, sheet_name=shop_name, index=False)
        pic_df.to_excel(w, sheet_name=pic_name, index=False)
        ocr_df.to_excel(w, sheet_name=orc_name, index=False)

def handle_shop_df(df:pd.DataFrame):
   
    df.sort_values(by=["sold","goods_name"],ascending=[False,False],inplace=True)
    df.drop_duplicates(subset=[item_id],inplace=True,ignore_index=True)
    df.sort_values(by=["sold"],ascending=False,inplace=True)
    
    df=assign_col_numbers(df,num_id)
    # print(df)

    return df

def org_main_dict_lst(org_data:dict)->list:
    if not org_data or "data" not in org_data:
        return 

    data=org_data["data"]
    item=data["item"]
    pic_url=item["images"]
    id=item[item_id]

    return [{item_id:id,"pic_url":url,"type":0,num_id:-1} for url in pic_url]
def json_main_df():
    results=[]
    
    for file in glob.glob(f"{main_dir}/*.json"):
        data=priority_read_json(file,encoding="utf-8-sig")
        if not data:
            continue
        results.extend(org_main_dict_lst(data))

    return pd.DataFrame(results)
    

def org_desc_dict_lst(html_content,id)->list:
    if not html_content :
        return 
    # 解析 HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # 找到所有 <div class="descV8-singleImage"> 下的 <img> 标签
    img_tags = soup.select('div.descV8-container div.descV8-singleImage img')

    # 提取 src 属性
    img_srcs = [img['data-src'] if   'data-src' in img.attrs else img["src"] for img in img_tags if 'src' in img.attrs or 'data-src' in img.attrs]
    return [{item_id:id,"pic_url":url,"type":1,num_id:-1} for url in img_srcs]

def xml_desc_df():
    results=[]
    for file in glob.glob(f"{desc_dir}/*.xml"):
        with open(file, 'r', encoding='utf-8') as f:
            html_content=f.read()
            item_id=os.path.basename(file).split(".")[0]
            results.extend(org_desc_dict_lst(html_content,item_id))
    return pd.DataFrame(results)


def concat_unique(dfs:list[pd.DataFrame],keys)->pd.DataFrame:

    return unique_df(concat_dfs(dfs),keys=keys)

def id_name_dict(df:pd.DataFrame)->dict:

    if df is  None or df.empty:
        return
    # 删除 goods_name 为空（NaN、''、' '）的行
    mask = (
        df['goods_name'].notna() &            # 过滤 NaN
        (df['goods_name'].str.strip() != '')   # 过滤空字符串或纯空格
    )
    df = df[mask].copy()
    
    #需要测试下
    result=df.set_index(item_id)[num_id].apply(lambda x:f"{x:03}").to_dict()

    return result

def handle_pic(df:pd.DataFrame,id_dict):
    df=update_col_nums(df,[item_id],num_id)
   
    df[name_id]=df.apply(lambda x:f"{id_dict.get(x[item_id])}_{x['type']}_{int(x[num_id]):03}",axis=1)

    return df


def download_pics(df:pd.DataFrame,cache_thread:ThreadPool,ocr_lst):
    cache_thread.start()
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
                
                ocr_path= os.path.join(ocr_pic_dir, Path(dest_path).name)
                if os.path.exists(ocr_path):
                    return

 
                cache_thread.submit(ocr_text,dest_path,ocr_path)
                pass
        except  Exception as e:
            logger.error("异常",f"原因：{e}",update_time_type=UpdateTimeType.STAGE)
        
    
    for index,row in df.iterrows():
        url=row["pic_url"]
        name=row[name_id]
        if not url or not name:
            continue
        file_path=os.path.join(org_pic_dir,f"{name}.jpg")
        cache_thread.submit(_download,fix_url(url),file_path)

def main():
    
    logger=logger_helper("获取信息","淘宝产品")
    logger.trace("开始")
    #读取
    org_df,pic_df,orc_df=read_xlsx_df()
    # print(org_df)

    
    # data_df=json_shop_df("木槿食养")

    # org_data=fetch_data()
    # if not org_data:
    #     return
    # data_df=org_to_df(org_data)
    
    
    
    org_df=handle_shop_df(concat_unique([org_df,json_shop_df("木槿食养")],keys=[item_id]))
    id_dict=id_name_dict(org_df)
    pic_df=handle_pic(concat_unique([pic_df,json_main_df(),xml_desc_df()],keys=["pic_url"]),id_dict)

    cache_thread=ThreadPool()
    ocr_lst=[]
    download_pics(pic_df,cache_thread,ocr_lst)

    cache_thread.shutdown()
    
    text_df=pd.DataFrame(ocr_lst)
    concat_unique([orc_df,text_df],keys=["name"])
    text_df.sort_values(by=["name"],ascending=True,inplace=True)
    
    # print(id_dict)
    #写入
    save_xlsx_df(org_df,pic_df,text_df)
    
    logger.info("完成",update_time_type=UpdateTimeType.ALL)
    


if __name__=="__main__":
    main()
    
    
    pass




