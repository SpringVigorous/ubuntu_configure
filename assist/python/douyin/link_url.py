import re
import sys
from douyin_tiktok_scraper.scraper import Scraper
from pathlib import Path
import os

import pandas as pd
import asyncio


root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )

from base import as_normal,logger_helper,UpdateTimeType
from base import write_to_txt,read_content_by_encode,path_equal

# 创建一个Scraper对象/Initialize a Scraper object
api = Scraper()
# 定义一个异步函数，用于获取抖音视频的下载链接/Define an asynchronous function to get the download link of a Douyin video
async def _douyin_url(video_url: str) -> str:
    
    logger=logger_helper("获取真实链接",video_url)
    
    url=None
    try:
        # 获取视频ID/Get video ID
        video_id = await api.get_douyin_video_id(video_url) 
        # 如果获取不到视频ID抛出异常/If the video ID cannot be obtained, an exception is thrown
        if  video_id:
            url= f"https://www.douyin.com/video/{video_id}" 
    except:
        pass
    
    if url:
        logger.trace("成功",url,update_time_type=UpdateTimeType.ALL)
    else:
        logger.error("失败",update_time_type=UpdateTimeType.ALL)
        
    return url


def douyin_urls(video_urls: list[str]) -> list[str]:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
        # 在每个线程中创建独立的 Semaphore 对象
    results=[]
    
    async def get_url(semaphore,url):
        async with semaphore:
            real_url= await _douyin_url(url)
            return real_url
    semaphore = asyncio.Semaphore(10)
    tasks = [get_url(semaphore,args) for args in video_urls]
    results=loop.run_until_complete(asyncio.gather(*tasks))
    loop.close()
    return results
    


def douyin_url(video_url: str) -> str:
    return as_normal(_douyin_url,video_url)

def extract_info(text):
    # 按换行符分割文本
    lines = text.split('\n')
    
    results = []
    logger=logger_helper("提取信息",text)
    for line in lines:
        # 处理包含“复制此链接”的行
        if '复制此链接' in line:
            # 剔除前25个字符（根据实际需求调整截取位置）
            processed_line = line[24:]
        else:
            processed_line = line
        
        # 使用正则匹配标题和链接
        match = re.search(
            r'(.*?)(https?://[^\s]+)',  # 匹配链接前所有内容作为标题
            processed_line
        )
        
        if match:
            raw_title = match.group(1).strip()
            logger.update_target(detail=line)
            link = match.group(2)
            
            # 清洗标题（去除开头的特殊字符）
            clean_title = re.sub(
                r'^[\d\.:/@\sA-Za-z]+',  # 匹配开头的数字、符号、空格
                '', 
                raw_title
            ).strip()
            
            data={"标题":clean_title,
                            "link":link,
                            }
            logger.trace("成功",f"\n{data}\n",update_time_type=UpdateTimeType.STEP)
            results.append(data)
    return results


def rearrage_links(wechat_messages:str,xlsx_path:str):
    
    json_path=os.path.splitext(xlsx_path)[0]+".json"
    
    json_df=None
    has_json=os.path.exists(json_path)
    if has_json:
        json_df=pd.read_json(json_path)

    
    
    # 执行提取
    lst = extract_info(wechat_messages)
    df=pd.DataFrame(lst)
    
    def set_urls(df):
        links=df["link"].tolist()
        df["url"]=douyin_urls(links)
    
    
    if has_json:
        merged = df.merge(json_df[['link']], 
                    on=['link'], 
                    how='left', 
                    indicator=True)
        left_df= merged[merged['_merge'] == 'left_only'].drop('_merge', axis=1)
        set_urls(left_df)

        df=pd.concat([json_df,left_df])
    else:
        set_urls(df)
        
    df.drop_duplicates(subset=["url"],keep="first",inplace=True)
    df.to_excel(xlsx_path,index=False)

    #输出到json中,下次方便操作
    df.to_json(json_path,orient="records",force_ascii=False)

def arrage_json(xlsx_path:str):
    if not os.path.exists(xls_path):
        return
    df=pd.read_excel(xlsx_path)
    if "flag" in df.columns:
        # 添加累积计数列
        df['index'] = df.groupby('flag', sort=False).cumcount() + 1
        df.dropna(subset=["index"],inplace=True)
        df["index"]=df["index"].astype(int)
        
        # if "name" not in df.columns:
        df["name"]=df.apply(lambda x:f"{x["flag"]}_{x['index']:03}",axis=1)
            
    json_path=os.path.splitext(xlsx_path)[0]+".json"
    df.to_json(json_path,orient="records",force_ascii=False)


def init_message(dest_path):
    wechat_messages="""
    清风细雨:
    7.64 03/08 d@a.aN dnq:/ 无锡最美的时刻到了 # 无锡 # 鼋头渚樱花 # 世界三大赏樱胜地 # 长春桥 实拍时间2025.3.25上午。  https://v.douyin.com/_MI6be4r2t0/ 复制此链接，打开Dou音搜索，直接观看视频！
！
    """
    write_to_txt(dest_path, wechat_messages,encoding="utf-8-sig")



if __name__=="__main__":
    message_dir=r"F:\worm_practice\douyin\素材\message"
    init_message_path=os.path.join(message_dir,"wechat_messages.txt")
    if False:
        init_message(init_message_path)
    xls_path=os.path.join(message_dir,"微信消息.xlsx")
    

    # arrage_json(xls_path)
    # exit()
    messages=[]
    
    for file in os.listdir(message_dir):
        if os.path.splitext(file)[1]!=".txt":
            continue
        file_path=os.path.join(message_dir,file)
        content=read_content_by_encode(file_path,source_encoding="utf-8-sig")
        if not content:
            continue
        messages.append(content)
        if not path_equal(init_message_path,file_path):
            os.remove(file_path)   
    
    wechat_messages="\n".join(messages)
    rearrage_links(wechat_messages,xls_path) 