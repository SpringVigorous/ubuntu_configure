from DrissionPage import WebPage
from DrissionPage.common import Actions
from pprint import pprint
import os
import time
import json
from requests.structures import CaseInsensitiveDict
import requests
import sys


from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from __init__ import *
from base.com_log import logger as logger
from base import setting as setting
from base.string_tools import sanitize_filename



from docx import Document
from docx.enum.style import WD_STYLE_TYPE

from queue import Queue
            
import asyncio 
import aiofiles
import aiohttp
        
        
import datetime
import pandas as pd

def convert_milliseconds_to_datetime(milliseconds):
    # 将毫秒时间戳转换为秒时间戳
    seconds = milliseconds / 1000.0
    
    # 将秒时间戳转换为 datetime 对象
    dt = datetime.datetime.fromtimestamp(seconds)
    
    # 格式化 datetime 对象为年月日时分秒格式
    formatted_date = dt.strftime('%Y-%m-%d %H:%M:%S')
    
    return formatted_date

def Num(thums):
    if type(thums)==str:
        thums=thums.strip()
    
        lst={"千":1000,"万":10000}
        scale:int=1
        
        for key in lst:
            if key in thums:
                scale*=lst[key]
                thums=thums.replace(key,"")
        
        return int(float(thums)*scale)  
    elif type(thums)==int:
        return thums
    else:
        return 0
    
    


class NoteInfo:
    def __init__(self,title,content,create_time,update_time,image_lst,author,thumbs,collected,shared,comment,note_id,current_time,video_lst):
        self.title=title
        self.content=content
        self.create_time=create_time    
        self.update_time=update_time  
        self.image_lst=image_lst
        self.author=author
        self.thumbs=thumbs
        self.collected=collected
        self.shared=shared
        self.comment=comment
        self.note_id=note_id
        self.current_time=current_time
        self.video_lst=video_lst
    @property
    def has_title(self):
        return bool(self.title)
    @property
    def has_images(self):
        return bool(self.image_lst)
    
    @property
    def has_video(self):
        return bool(self.video_lst)
    
    @property
    def has_content(self):
        return bool(self.content)
    
    @property
    def has_author(self):
        return bool(self.author)
    
    @property
    def has_thumbs(self):
        return bool(self.thumbs)
    
    @property
    def has_collected(self):
        return bool(self.collected)
    
    @property
    def has_shared(self):
        return bool(self.shared)
    
    @property
    def has_comment(self):
        return bool(self.comment)
    
    @property
    def has_note_id(self):
        return bool(self.note_id)
    
    @property
    def has_create_time(self):
        return bool(self.create_time)
    
    @property
    def has_update_time(self):
        return bool(self.update_time)
    
    @property
    def has_current_time(self):
        return bool(self.current_time)
    
    async def write_to_notepad(self,root_dir,cur_index):
       
        cur_dir=os.path.join(root_dir,f"{cur_index}_{self.title}")
        dest_note_path=os.path.join(cur_dir,  f"{self.title}.txt")
        dest_image_dir=os.path.join(cur_dir,"images/")
        dest_video_dir=os.path.join(cur_dir,"videos/")
        os.makedirs(os.path.dirname(dest_image_dir),exist_ok=True)
        os.makedirs(os.path.dirname(dest_video_dir),exist_ok=True)
        dest_image_lst=[os.path.join(dest_image_dir,f"{i+1}.jpg") for i in range(len(self.image_lst))]
        os.makedirs(os.path.dirname(dest_note_path),exist_ok=True)
        
        #文本
        async with  aiofiles.open(dest_note_path,"w",encoding="utf-8") as f:
            contents=[
            f"title:{self.title}"
            f"note_id:{self.note_id}",
            f"current_time{self.current_time}",
            f"create_time{self.create_time}",
            f"update_time{self.update_time}",
            f"image_lst:{"\n".join(dest_image_lst)}",
            f"author:{self.author}",
            f"thumbs:{self.thumbs}",
            f"collected:{self.collected}",
            f"shared:{self.shared}",
            f"comment:{self.comment}",
            f"content:{self.content}"
            ]
            await f.write('\n'.join(contents)+"\n")
            
            
        #图片
        for i in range(len(self.image_lst)):
            url=self.image_lst[i]
            dest_path=dest_image_lst[i]
            
        async  with aiohttp.ClientSession() as clientSession:
            async with clientSession.get(url=url) as responds:
                async with aiofiles.open(dest_path,"wb") as f:
                    await f.write(await responds.content.read())

        #视频
        for index,video_url in  enumerate( self.video_lst):

            video_name=f"{index+1}.mp4"
            async  with aiohttp.ClientSession() as clientSession:
                async with clientSession.get(video_url) as video_responds:

                    video_dest_path=os.path.join(dest_video_dir,video_name)
                    async with aiofiles.open(video_dest_path,"wb") as f:
                        await f.write(await video_responds.content.read())
    
    

async def ParseOrgNote(raw_data):
    # raw_data=json.loads(body)
    
    await asyncio.sleep(.1)
    
    note_data=raw_data["data"]
    note_info=note_data["items"][0]
    
    id=note_info["id"]
    model_type=note_info["model_type"]
    note_card=note_info["note_card"]
    topics=[ tag["name"] for tag in note_card["tag_list"]] if "tag_list" in note_card else []
    if not topics:
        return None
    
    content=note_card["desc"] if "desc" in note_card else ""
    user=note_card["user"]
    user_id=user["user_id"]
    user_name=user["nickname"]

    user_icon=user["avatar_url"] if "avatar_url" in user else ""
    interact_info=note_card["interact_info"]
    liked_count=Num(interact_info.get("liked_count"))
    collected_count=Num(interact_info.get("collected_count",0))
    share_count=Num(interact_info.get("share_count",0))
    comment_count=note_info.get("comment_count",0)
    
    image_urls=[item["url_default"]  for item in note_card["image_list"]]  if "image_list" in note_card else []
    create_time=convert_milliseconds_to_datetime(note_card["time"])
    update_time=convert_milliseconds_to_datetime(note_card["last_update_time"])
    note_id=note_card["note_id"]
    title=sanitize_filename(note_card["title"])
    current_time=convert_milliseconds_to_datetime(note_data["current_time"])
    video_lst=[video["master_url"] for video in note_card["video"]["media"]["stream"]["h264"]] if "video" in note_card else []

    return  NoteInfo(title=title,
                    content=content,
                    create_time=create_time,
                    update_time=update_time,
                    image_lst=image_urls,
                    author=user_name,
                    thumbs=liked_count,
                    collected=collected_count,
                    shared=share_count,
                    comment=comment_count,
                    note_id=note_id,
                    current_time=current_time,
                    video_lst=video_lst)


class Section:
    def __init__(self,sec,yVal,id,already):
        self.sec=sec
        self.yVal=yVal
        self.id=id
        self.already=already



class SectionManager:
    def __init__(self,wp):
        self.wp=wp
        self.cur_secs=[]
        self.secs=[]
        self.cur_index=0
        
    def __set_secs(self,secs:list):
        self.cur_secs=secs
        
        for sec in self.cur_secs:
            sec_ids=[sec.id for sec in self.secs]
            if sec.id not in sec_ids:
                self.secs.append(sec)
            else:
                self.secs[sec_ids.index(sec.id)]=sec
        
        # self.secs.extend(self.cur_secs)

    def update(self):
        
        # await asyncio.sleep(.3)
        time.sleep(.3)
        
        org_secs=self.wp.eles("xpath://section")
        sorted(org_secs,key=lambda x:x.rect.midpoint[1])
        # _backend_id 13
        
        self.backends=[sec._backend_id for sec in org_secs]
        self.note_ids=[sec.raw_text for sec in org_secs]
        
        secs=[Section(sec,sec.rect.midpoint[1],sec.raw_text,False)   for sec in org_secs]
        if self.secs:
            for sec in secs:
                org=self.get_by_id(sec.id)
                if org:
                    sec.already=org.already
        
        
        # self.secs.extend(secs)
        self.__set_secs(secs)
    def get_by_id(self ,id):
        secs=[sec for sec in self.secs if sec.id==id]
        return secs[0] if secs else None
        

    
    def next(self):
        # self.update()
        for sec in self.cur_secs:
            if not sec.already:
                sec.already=True
                self.cur_index=self.cur_secs.index(sec)
                yield sec.sec
     
    def resume_cur(self):
        if self.cur_index<len(self.cur_secs):
            self.cur_secs[self.cur_index].already=False
        
        
    def count(self):
        # self.update()
        return sum([ 0 if sec.already else 1  for sec in self.cur_secs ])


        


class RedBookSearch:
    def __init__(self,wp:WebPage,theme_name:str,root_dir:str=setting.redbook_notes_dir,search_count:int=200,queue_count:int=100) -> None:
        self.wp=wp
        self.theme_name=theme_name
        self.root_dir=root_dir
        self.search_count=search_count
        self.data_queue=Queue(maxsize=queue_count)
        self.cur_index=0
        self.stoped=False
        
        
        pass
    @property
    def ThemeDir(self):
        return os.path.join(self.root_dir,self.theme_name)
    
    #同步进行
    def SearchTheme(self):
        self.wp.get('https://www.xiaohongshu.com/')
        
        time.sleep(5)
        
        search_input = self.wp.ele('xpath://input[@class="search-input"]')
        search_input.clear()
        search_input.input(f'{self.theme_name}\n')
        time.sleep(.4)

        
        seach_button=self.wp.ele('xpath://div[@class="search-icon"]')
        if not seach_button:
            sys.exit(0)
        self.wp.ele('xpath://div[@class="search-icon"]').click()

    def StopListen(self):
        self.wp.listen.stop()

    def CloseBrowser(self):
        self.wp.quit()

        
    async def SearchNotes(self):

        self.wp.listen.start(['web/v1/search/notes',"api/sns/web/v1/feed"]) 
        packet = self.wp.listen.wait()
        cur_dir=self.ThemeDir
        os.makedirs(cur_dir,exist_ok=True)


        sec_i=0
        
        secManager=SectionManager(self.wp)
        secManager.update()
        while (secManager.count())>0:
            
            if sec_i>=self.search_count:
                self.stoped=True
                break
            # secManager.update()
            

            sec=next(secManager.next()) 
            if not sec:
                continue
            await asyncio.sleep(1)
            
            try:
                sec.click()
            except:
                secManager.resume_cur()
                secManager.update()
                continue
            pack=self.wp.listen.wait()


            self.data_queue.put(pack.response.body)
            sec_i+=1
            await asyncio.sleep(1)
            # with open(os.path.join(cur_dir,f"{sec_i:04d}.json"), "w", encoding="utf-8") as f:
            #     json.dump(pack.response.body,f,indent=4,ensure_ascii=False)


            close_flag=self.wp.ele('xpath://div[@class="close close-mask-dark"]')
            if close_flag:
                close_flag.click()
                
            
                

    async def HandleNotes(self):
        lst=[]
        
        while not (self.stoped and self.data_queue.empty()):
            if self.data_queue.empty():
                await asyncio.sleep(.1)
                continue
            
            data=self.data_queue.get()
            noteinfo= await ParseOrgNote(data)
            if noteinfo:
                lst.append(noteinfo)
                # await noteinfo.write_to_notepad(self.ThemeDir,self.cur_index)
            self.cur_index+=1
        if lst:
            df=pd.DataFrame([info.__dict__ for info in lst], columns=lst[0].__dict__.keys())
            return df

    def __CreateNotes():
        
        index=0
        for root, dirs, files in os.walk(setting.redbook_history_dir):
            for name in files:
                if not name.endswith(".json"):
                    continue
                with open(os.path.join(root,name),"r",encoding="utf-8") as f:
                    content= f.read()
                    noteinfo= ParseOrgNote(content)
                    if noteinfo:
                        noteinfo.write_to_notepad(setting.redbook_notes_dir,index)
                    index+=1
                    
class RedBookSearchs:
    def __init__(self,themes:list,root_dir:str=setting.redbook_notes_dir,search_count:int=5,queue_count:int=100) -> None:
        self.wp=WebPage()
        self.themes=themes
        self.root_dir=root_dir
        self.search_count=search_count
        self.queue_count=queue_count
        
    def InfoToExcel(self,root_dir, pds:list):
        outPath = os.path.join(root_dir,"notes_tab.xlsx")
        with pd.ExcelWriter(outPath) as writer:
            for theme,df in pds:
                if not df is None:
                    df.to_excel(writer, sheet_name=theme)
 
 
        
    #无法异步处理，浏览器只能有一个
    async def AsyncDumps(self):
        sem= asyncio.Semaphore( os.cpu_count()+4 )
        async def fetch_theme(theme):
            async with sem:
                search=RedBookSearch(None,theme,self.root_dir,self.search_count,self.queue_count)
                search.SearchTheme()
                
                tasks=[search.SearchNotes(),search.HandleNotes()]
                task_list=[asyncio.create_task(task) for task in tasks]
                results= await asyncio.gather(*task_list)
                search.StopListen()
                return results[1]
            
        
        tasks=[fetch_theme(theme) for theme in self.themes]
        results= await asyncio.gather(*tasks)
        
        dfs=[result for result in results if not result is None]
        self.InfoToExcel(self.root_dir,dfs)
        
    async def Dumps(self):
        
        dfs=[]
        for theme in self.themes:
            search=RedBookSearch(self.wp,theme,self.root_dir,self.search_count,self.queue_count)
            search.SearchTheme()
            
            tasks=[search.SearchNotes(),search.HandleNotes()]
            task_list=[asyncio.create_task(task) for task in tasks]
            results= await asyncio.gather(*task_list)
            df= results[1]
            if not df is None:
                dfs.append((theme,df) )
                json_dir=os.path.join(self.root_dir,theme,"json/")
                os.makedirs(json_dir,exist_ok=True)

                df.to_json(os.path.join(json_dir,f"{theme}.json"), orient="records")
            search.StopListen()
            # search.CloseBrowser()
            
        self.InfoToExcel(self.root_dir,dfs)
        
        
        """
        问题： 有重复项目
        """
if __name__ == '__main__':
    wp=WebPage()
    themes=["四神汤","薏米茶",'八宝茶']
    
    redbook=RedBookSearchs(themes=themes)
    asyncio.run(redbook.Dumps()) 
    
