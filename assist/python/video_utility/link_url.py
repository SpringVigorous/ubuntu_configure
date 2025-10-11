import re
import sys
from douyin_tiktok_scraper.scraper import Scraper
from pathlib import Path
import os

import pandas as pd
import asyncio






from base import as_normal,logger_helper,UpdateTimeType,mp4_files
from base import write_to_txt,read_content_by_encode,path_equal,unique

from base.video_utility.dy_utility import dy_root,OrgInfo

def now_pd_str():
    return f"{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}"
class MessageManager:
    # 创建一个Scraper对象/Initialize a Scraper object
    api = Scraper()
    def __init__(self) -> None:
        pass

    @staticmethod
    def save_json(df:pd.DataFrame):
        #输出到json中,下次方便操作
        df.to_json(dy_root.message_json_file,orient="records",force_ascii=False)

    @staticmethod
    def sort_df(df:pd.DataFrame):
        #排序
        df.sort_values(by=["name"],inplace=True)
    
    @staticmethod
    def save_xlsx(df:pd.DataFrame):
        df.to_excel(dy_root.message_xls_file,index=False)
    
    
    @staticmethod
    def load_xlsx()->pd.DataFrame:
        file_path=dy_root.message_xls_file
        return pd.read_excel(file_path) if os.path.exists(file_path) else pd.DataFrame()
    
    @staticmethod
    def load_json()->pd.DataFrame:
        file_path=dy_root.message_json_file
        return pd.read_json(file_path) if os.path.exists(file_path) else pd.DataFrame()
    
    @staticmethod
    def load_txt(message_txt):
        lst = MessageManager.extract_message(message_txt)
        df=pd.DataFrame(lst)
        return df
    
    
    
    # 定义一个异步函数，用于获取抖音视频的下载链接/Define an asynchronous function to get the download link of a Douyin video
    @staticmethod
    async def _proto_url(video_url: str) -> str:
        
        logger=logger_helper("获取真实链接",video_url)
        
        url=None
        try:
            # 获取视频ID/Get video ID
            video_id = await MessageManager.api.get_douyin_video_id(video_url) 
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


    @staticmethod
    def proto_urls(video_urls: list[str]) -> list[str]:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
            # 在每个线程中创建独立的 Semaphore 对象
        results=[]
        
        async def get_url(semaphore,url):
            async with semaphore:
                real_url= await MessageManager._proto_url(url)
                return real_url
        semaphore = asyncio.Semaphore(10)
        tasks = [get_url(semaphore,args) for args in video_urls]
        results=loop.run_until_complete(asyncio.gather(*tasks))
        loop.close()
        return results
        



    @staticmethod
    def is_title_style(s):
        # 正则表达式解释：
        # ^0-9a-zA-Z\:@\\ 表示允许的字符范围：数字、英文大小写字母、:@\ 以及英文标点符号
        # 如果字符串中存在至少一个不属于上述范围的字符，则返回 True
        pattern = r'[^0-9a-zA-Z:@\\./]'  # \s 表示允许空白符，如果不需要则移除
        return bool(re.search(pattern, s))

    @staticmethod
    def split_title(title):
        raw_key=""
        keys=[]
        if "#" in title:
            index=title.index("#")
            raw_key=title[index:]
            keys=unique(re.findall(r'\s?#\s+(\S+)',raw_key))
            title=title[:index].strip()
            
            
        if not title and raw_key:
            """# 绿樱花 绿色的樱花，像是从童话世界中走来，带着..."""
            for key in keys:
                raw_key=re.sub(r'\s?#\s+'+key," ",raw_key)
            
            title=raw_key.replace("#","").strip()
            
        return title,",".join(keys)

    @staticmethod
    def extract_line(line):
        if not line:  # 跳过空行
            return
            
        # 使用正则匹配标题和链接
        match = re.search(
            r'(.*?)\s+(https?://\S+)(?:.*\btag\s?:\s?(\S+))?(?:.*\bsec\s?:\s?(\d+))?.*$',  # 匹配链接前所有内容作为标题
            line
        )
        
        if not match:
            return
        title = match.group(1).strip().strip()

        link = match.group(2).strip()
        tag=match.group(3) or ""
        sec=match.group(4) or -1
        # 清洗标题（去除开头的特殊字符）
        title=title
        keys=[]
        raw_key=None
        if "#" in title:
            index=title.index("#")
            raw_key=title[index:]
            keys=re.findall(r'\s?#\s+(\S+)',raw_key)
            title=title[:index].strip()
        
        if '去抖音看看' in title:
            title_match=re.search(r'.*去抖音看看[^】]+】(.*)', title)
            if title_match:
                title=title_match.group(1).strip()
        else:
            title_lst= list(filter(lambda x:MessageManager.is_title_style(x), title.split()))
            title=" ".join(title_lst)
            
            #最后一个空白间隔为标题
            if not title_lst:
                title_lst=title.split()
                title=title_lst[-1] if title_lst else ""
        if not title and raw_key:
            """# 绿樱花 绿色的樱花，像是从童话世界中走来，带着..."""
            for key in keys:
                raw_key=re.sub(r'\s?#\s+'+key," ",raw_key)
            
            title=raw_key.strip()
        
        data={  "标题":title.replace("#","").strip(),
                "keys":",".join(unique(keys)),
                "link":link,
                "tag":tag,
                "craw_time":now_pd_str,
                "sec":int(sec)
                }
        
        return data


    @staticmethod
    def extract_message(text):
        # 按换行符分割文本
        lines = text.split('\n')
        results = {}
        logger=logger_helper("提取信息",text)
        for line in lines:
            logger.update_target(detail=line)
            data=MessageManager.extract_line(line)
            if not data:
                continue
            logger.trace("成功",f"\n{data}\n",update_time_type=UpdateTimeType.STEP)
            results[data["link"]]=data

        return [data for _,data in results.items()]

    
    @staticmethod
    def remove_duplicates(df):
        # 根据 url 列是否为空进行分组
        df_with_url = df[df['url'].notna()]
        no_url_has_link_mask=df["url"].isna()& df["link"].notna()
        no_url_no_link_mask=df["url"].isna()& df["link"].isna()
        
        df_without_url_has_link = df[no_url_has_link_mask]
        df_without_url_no_link = df[no_url_no_link_mask]

        # 对 url 列有值的数据根据 url 列去重
        df_with_url = df_with_url.drop_duplicates(subset='url',keep="first",)

        # 对 url 列为空的数据根据 link 列去重
        df_without_url_has_link = df_without_url_has_link.drop_duplicates(subset='link',keep="first",)
        
        df_without_url_no_link = df_without_url_no_link.drop_duplicates(subset='name',keep="first",)

        # 过滤掉空的 DataFrame
        non_empty_dfs =[item for item in  [df_with_url,df_without_url_has_link,df_without_url_no_link] if not item.empty]
        # 合并两部分数据
        if non_empty_dfs:
            result = pd.concat(non_empty_dfs)
        else:
            result = pd.DataFrame(columns=df.columns)

        return result

    #json和message是重要参数，两者合并后输出到xlsx中,同时重新写入.json中
    @staticmethod
    def from_chat_message(wechat_messages:str):
        json_df=MessageManager.load_json()
        has_json=not json_df.empty
        # 执行提取
        df=MessageManager.load_txt(wechat_messages)

        def fetch_urls(df:pd.DataFrame):
            
            null_mask=df["url"].isna()
            if null_mask.empty:
                return
            links=df.loc[null_mask,"link"].tolist()
            df.loc[null_mask,"url"]=MessageManager.proto_urls(links)
        if has_json :
            if  not df.empty:
                merged = df.merge(json_df[['link',"url"]], 
                            on=['link'], 
                            how='left', 
                            indicator=True)
                left_df= merged[merged['_merge'] == 'left_only'].drop('_merge', axis=1)
                fetch_urls(left_df)

                df=pd.concat([json_df,left_df])
            else:
                df=json_df
        else:
            fetch_urls(df)
            

        MessageManager.remove_duplicates(df)
        # df.drop_duplicates(subset=["url"],keep="first",inplace=True)

        MessageManager.update_name(df)
        MessageManager.update_download_flag(df)
        
        MessageManager.fix_data_type(df)
        
        # MessageManager.update_video_name(df)
        MessageManager.save_json(df[df["url"].notna()])
        #尽量别排序
        # MessageManager.sort_df(df)
        MessageManager.save_xlsx(df)

    


    @staticmethod
    def keys_from_title(df):
            
        # 步骤1：找到keys列为空的行（假设空值为NaN）
        mask = df['keys'].isna()

        # 步骤2：分割title列，按第一个空格分割成两部分
        split_result = df.loc[mask, '标题'].apply(lambda x: MessageManager.split_title(x)).tolist()
        # print(split_result)
        # 步骤3：覆盖原DataFrame的标题和keys列
        df.loc[mask, '标题'] = [item[0] for item in split_result]
        df.loc[mask, 'keys'] = [item[1] for item in split_result]
    @staticmethod
    def unique_keys(df):
        def unique_key(x:str):
            if not x:
                return x
            return ",".join(unique(x.split(","))) 
        df["keys"]=df["keys"].apply(lambda x:unique_key(x))


    @staticmethod
    def update_download_status(df:pd.DataFrame):
        download_lst=[Path(file).name for file in mp4_files(dy_root.org_root)]
        df["downloaded"]=df["name"].apply(lambda x:1 if x in download_lst else 0)
        df["downloaded"]=df["downloaded"].astype(int)
    
    @staticmethod
    def fix_data_type(df:pd.DataFrame):
        
        df["craw_time"]=df["craw_time"].fillna("")
        df["craw_time"]=df["craw_time"].astype(str)
        
        df["downloaded"]=df["downloaded"].fillna(0)
        df["downloaded"]=df["downloaded"].astype(int)
        
        df["sec"]=df["sec"].fillna(-1)
        df["sec"]=df["sec"].astype(int)
        
    
    @staticmethod
    def update_download_flag(df:pd.DataFrame):
        download_lst=[Path(file).stem for file in mp4_files(dy_root.org_root)]
        df["downloaded"]=df["name"].apply(lambda x:1 if x in download_lst else 0)

    @staticmethod
    def update_name(df:pd.DataFrame,mask=None):
        # 筛选出需要处理的行：name为空
        if mask is None:
            mask = df['name'].isna() & df["tag"].notna()

        if not mask.any():
            return df
        
        # 将video_num列转换为数值类型，非数值转为NaN
        df['video_num'] = pd.to_numeric(df['video_num'], errors='coerce')
        
        # 按tag分组处理
        grouped = df[mask].groupby('tag')
        for tag, group in grouped:
            # print(group)
            
            # 获取该tag下所有现有的非空video_num
            existing_video_nums = set(
                df.loc[(df['tag'] == tag) & df['video_num'].notna(), 'video_num'].astype(int)
            )
            # 处理该tag下的每一行
            for idx in group.index:
                min_missing = 1
                while min_missing in existing_video_nums:
                    min_missing += 1
                # 更新video_num和name
                df.at[idx, 'video_num'] = min_missing
                df.at[idx, 'name'] = f"{tag}_{min_missing:03}"
                existing_video_nums.add(min_missing)
        
        return df

    @staticmethod
    def update_name_old(df:pd.DataFrame):
        """
        DataFrame类型变量df,包含name和tag,video_num三列，其中name列可能为空，tag列不为空，
        如果name为空，重新计算video_num值（当天tag的累计计数),由于这个df的数据是动态变化的，可以被删除了某些行，导致video_num值不连续，
        但是针对已经存在的行，video_num值不需要重新赋值，只需要对为赋值 video_num的行进行赋值即可（其值是 1到tag的累计计数 中缺少的最小整数值）
        然后对name为空的进行赋值即 name=tag+"_"+video_num,其中video_num为当前行的值


        Args:
            df (pd.DataFrame): _description_

        Returns:
            _type_: _description_
        """
        name_mask=df["name"].isna() and df["tag"].notna()
        if name_mask.empty:
            return
        tag_df=df.loc[name_mask,"tag"]
        tag_lst=unique(tag_df.tolist())
        print(tag_lst)
        return
        # 添加累积计数列
        tag_df.groupby('tag', sort=False)
        
        
        df['video_num'] = df.groupby('tag', sort=False).cumcount() + 1
        df.dropna(subset=['video_num'],inplace=True)
        df['video_num']=df['video_num'].astype(int)
        
        
        
        df["name"]=df.apply(lambda x:f"{x["tag"]}_{x['video_num']:03}",axis=1)
        
        


        #老版本中keys没有赋值，因此要调用下，重新赋值，新版本就不需要了
        # keys_from_title(df)
        # unique_keys(df)
        return df



    #从excel中根据tag和index重新生成name，并输出到json中，方便下次操作
    @staticmethod
    def update_json():
        df=MessageManager.load_xlsx()
        if df.empty:
            return
        MessageManager.fix_data_type(df)
        
        MessageManager.update_name(df)
        MessageManager.update_download_flag(df)
        MessageManager.save_json(df)
    @staticmethod
    def get_message_txts():
        message_dir=dy_root.message_root
        #excel数据->json
        # update_json()
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
            if not path_equal(dy_root.message_base_file,file_path):
                os.remove(file_path)  
            else:
                #清空内容
                write_to_txt(dy_root.message_base_file,"",encoding="utf-8-sig") 

        return "\n".join(messages)
    
    @staticmethod
    def update_messages():
        wechat_message=MessageManager.get_message_txts()
        MessageManager.from_chat_message(wechat_message) 
    
    @staticmethod
    def update_from_files():
        
        df=MessageManager.load_json()
        names=df["name"].to_list()
        
        datas=[]
        
        for file in mp4_files(dy_root.org_root):
            info=OrgInfo(file)
            org_name=info.org_name
            
            if org_name in names:
                continue
            datas.append({
                "name":org_name,
                "tag":info.series_name,
                "craw_time":now_pd_str(),
                "downloaded":1,
                "sec":-1,
                "video_num":info.series_number
            })
        
        if datas:
            df1=pd.DataFrame(datas)
            df=pd.concat([df,df1],ignore_index=True)
            df=MessageManager.remove_duplicates(df)
            
            MessageManager.save_json(df)
            MessageManager.save_xlsx(df)

    
def main():
    # MessageManager.update_messages()
    # MessageManager.update_json()
    MessageManager.update_from_files()

if __name__=="__main__":
    main()