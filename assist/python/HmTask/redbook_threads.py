from queue import Queue,Empty
import sys
sys.path.append("..")
sys.path.append(".")

from base_task import ThreadTask,clear_queue
import threading
import time
from DrissionPage import WebPage


from __init__ import *
from base.com_log import logger as logger,usage_time
from base import setting as setting
from base.string_tools import sanitize_filename,time_flag


from HmTask.redbook_tools import *

from docx import Document
from docx.enum.style import WD_STYLE_TYPE

import pandas as pd
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor , wait, ALL_COMPLETED
from collections import namedtuple


JsonData=namedtuple("JsonData",["theme","json_data"]) # str,dict


RawData=namedtuple("RawDataQueue",["file_path","json_data"]) #str,dict
NotesData=namedtuple("NotesData",["theme","pd"])  #  str, pd

ThemesData=namedtuple("ThemesData",["file_path","datas"]) # str,list[NotesData]

global_theme_queue= Queue()
global_json_queue=Queue() #JsonData or ThemesAllFlag
global_raw_data_queue=Queue() #RawData
global_note_queue=Queue() #NoteInfo
global_notes_queue=Queue() #NotesData


stop_interact_event=threading.Event()
stop_parse_event=threading.Event()
stop_hanle_event=threading.Event()


class Interact(ThreadTask):
    def __init__(self, root_dir:str=setting.redbook_notes_dir,search_count:int=10):
        super().__init__(global_theme_queue,output_queue=None,stop_event=stop_interact_event)



        self.wp=WebPage()
        self.root_dir=root_dir
        self.search_count=search_count
        url='https://www.xiaohongshu.com/'
        
        self.wp.get(url)

        

        time.sleep(5) #初次等待登录
        
    def final_except(self)->bool:
        return False
    
    def _each_except_after(self,data):    
        pass
    
    def _each_run_after(self,data):

        pass
    
    def _final_run_after(self):
        stop_parse_event.set()
        pass
    
    def handle_data(self, theme):
        start_time=time.time()
        

        theme_info=f"【{theme}】"
        
        target=f"采集{theme_info}"
        
        logger.info(record_detail( target,"开始","……"))
        

        
        stop_event = threading.Event()
        theme_dir=os.path.join(self.root_dir, theme)
        os.makedirs(theme_dir, exist_ok=True)

        i = 0
        try:
            #测试异常
            # raise FileNotFoundError("helllo")
        
            #搜索输入框
            search_input = self.wp.ele('xpath://input[@class="search-input"]')
            search_input.clear()
            search_input.input(f'{theme}\n')
            time.sleep(.4)

            #搜索按钮
            seach_button=self.wp.ele('xpath://div[@class="search-icon"]')
            if not seach_button:
                sys.exit(0)
            self.wp.ele('xpath://div[@class="search-icon"]').click()
            self.wp.listen.start(['web/v1/search/notes',"api/sns/web/v1/feed"]) 
            packet = self.wp.listen.wait()
            secManager=SectionManager(self.wp)
            secManager.update()

            while i < self.search_count:
                sec=next(secManager.next()) 
                if not sec:
                    continue
                time.sleep(.1)
                
                # if i>1:
                #     raise Exception("测试异常")
                try:
                    sec.click()
                except:
                    secManager.resume_cur()
                    secManager.update()
                    continue
                pack=self.wp.listen.wait()
                body=pack.response.body
                if body:
                    body["my_link"]=self.wp.url
                    data=JsonData(theme=theme,json_data=body)
                    global_json_queue.put(data)    #整理到内部队列
                    i += 1
                    
                close_flag=self.wp.ele('xpath://div[@class="close close-mask-dark"]')
                if close_flag:
                    try:
                        close_flag.click()
                    except:
                        continue
            
        except Exception as e:
            logger.error(record_detail(target,f"异常【{e}】", f"共采集{i}个，{usage_time(start_time)}"))
            clear_queue(self.InputQueue)
            self.Stop() #关闭本身
            stop_parse_event.set()#依赖本任务的输出结果的事件，也要设置
            return 
            
        logger.info(record_detail(target,f"完成", f"共采集{i}个，{usage_time(start_time)}"))
      
#主要用于写入临时文件，队列信息为（file_path,content,mode,encoding）
class WriteFile(ThreadTask):
    def __init__(self):
        super().__init__(input_queue=global_raw_data_queue, stop_event=stop_hanle_event)
        
    def handle_data(self, file_info):
        file_path,content=file_info
        read_write_sync(content,file_path,mode="w",encoding="utf-8-sig")
        
    def _each_run_after(self,data):
        pass
    def _final_run_after(self):
        pass

class NoteDir:
    def __init__(self,dest_dir:str=setting.redbook_notes_dir):
        self.dest_dir=dest_dir


    
    @property
    def CurName(self):
        return self.CurPath.name
    
    @property
    def CurPath(self):
        return Path(self.dest_dir)

    @property
    def ParentDir(self):

        return self.CurPath.parent


class Parse(ThreadTask,NoteDir):
    def __init__(self, dest_dir=setting.redbook_notes_dir):
        super().__init__(input_queue=global_json_queue, output_queue=global_note_queue, stop_event=stop_parse_event)
        NoteDir.__init__(self,dest_dir=dest_dir)
        self.datas_queue=global_notes_queue
        self.datas_lst:list[NoteInfo]=[] #同一个主题
        self.output_file_queue=global_raw_data_queue

        self.cur_theme=""
        self.themes_data:list[NotesData]=[] #多个主题
        
    def _each_run_after(self,data):
        pass

    def _final_run_after(self):
        start_time=time.time()
        target="汇总excle文件 {outPath}"
        logger.trace(record_detail(target,"开始", "..."))
        self.handle_theme()
        stop_hanle_event.set()
        #Excle输出
        outPath = os.path.join(self.CurPath,f"{time_flag()}.xlsx")
        with pd.ExcelWriter(outPath) as writer:
            for info in self.themes_data:
                if not info.pd is None:
                    info.pd.to_excel(writer, sheet_name=info.theme)

        logger.trace( record_detail(target,"写入成功",usage_time(start_time)))
        pass
    
    def handle_theme(self):
        if not self.datas_lst:
            return
        df=pd.DataFrame([info.__dict__ for info in self.datas_lst], columns=self.datas_lst[0].__dict__.keys())
        if not df is None:
            df.sort_values(by=["thumbs","create_time"], ascending=[False, True],inplace=True)
        dest_data=NotesData(theme=self.cur_theme,pd=df)
        self.datas_queue.put(dest_data)
        self.themes_data.append(dest_data)
        self.datas_lst.clear()
        
        
    
    
    def handle_data(self, data:JsonData):

        theme,raw_data=data.theme,data.json_data
        if not self.cur_theme:
            self.cur_theme=theme
        elif self.cur_theme != theme:  #切换主题
            self.handle_theme()
            self.cur_theme=theme
            pass    
        
        link=raw_data.get("my_link","")
        
        if not "data" in raw_data:
            return None
        
        note_data=raw_data["data"]
        note_info=note_data["items"][0]
        
        id=note_info["id"]
        model_type=note_info["model_type"]
        note_card=note_info.get("note_card",None)
        if not note_card:
            return None
        type=note_card.get("type","")

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
        if not title:
            title=note_id #str(uuid4())
        current_time=convert_milliseconds_to_datetime(note_data["current_time"])
        video_lst=[video["master_url"] for video in note_card["video"]["media"]["stream"]["h264"]] if "video" in note_card else []

        noteinfo= NoteInfo(title=title,
                        content=content,
                        create_time=create_time,
                        update_time=update_time,
                        image_urls=image_urls,
                        author=user_name,
                        thumbs=liked_count,
                        collected=collected_count,
                        shared=share_count,
                        comment=comment_count,
                        note_id=note_id,
                        current_time=current_time,
                        video_urls=video_lst,
                        type=type,link=link)
        
        
        
        
        
        
        theme_path=os.path.join(self.CurPath,theme)
        noteinfo.set_root_dir(theme_path )
        json_path=os.path.join(theme_path, noteinfo.title,f"{noteinfo.title}.json")
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        
        
        self.output_file_queue.put(RawData(file_path=json_path, json_data= json.dumps(raw_data,ensure_ascii=False,indent=4)) )
        

        #缓存到notes
        self.datas_lst.append(noteinfo)
        
        return noteinfo


class InputTask(ThreadTask,NoteDir):
    def __init__(self, input_queue,  stop_event=None,dest_dir=setting.redbook_notes_dir):
        super().__init__(input_queue=input_queue, stop_event=stop_event)
        NoteDir.__init__(self,dest_dir=dest_dir)

    def _each_run_after(self,data):
        pass
    def _final_run_after(self):
        pass

class HandleNote(InputTask):
    def __init__(self, dest_dir=setting.redbook_notes_dir):
        super().__init__(input_queue=global_note_queue, stop_event=stop_hanle_event,dest_dir=dest_dir)
    def handle_data(self, noteinfo:NoteInfo):
        
        asyncio.run(noteinfo.handle_note())
        
#以下两个可以并行
class HandleTheme(InputTask):
    def __init__(self, dest_dir=setting.redbook_notes_dir):
        super().__init__(input_queue=global_notes_queue, stop_event=stop_hanle_event,dest_dir=dest_dir)

    def _final_run_after(self):
        pass
        
    def handle_data(self, theme_pds):
        theme,df=theme_pds.theme,theme_pds.pd
        #临时数据，缓存使用、
        dict_data=df.to_dict("records")
        to_theme_word(theme_name=theme,root_dir=self.CurPath,dict_data=dict_data)





class App:
    def __init__(self) :
       pass

    def run(self,themes:list,search_count=20):
        theme_info=f'{"、".join(themes)}'
        target=f"采集-{theme_info}"
        
        
        logger.info(record_detail(target,"开始","") )

        start_time = time.time()
        


        root_dir=setting.redbook_notes_dir
        
        interact=Interact(root_dir=root_dir,search_count=search_count)
        parse=Parse(dest_dir=root_dir)
        handle_note=HandleNote(dest_dir=root_dir)
        handle_theme=HandleTheme(dest_dir=root_dir)
        file_writer=WriteFile()
        
        
        for theme in themes:
            global_theme_queue.put(theme)
        
        interact.start()
        parse.start()
        handle_note.start()
        file_writer.start()
        handle_theme.start()
        
        stop_interact_event.set()
        interact.join()
        parse.join()
        
        file_writer.join()
        # theme_queue.join()

        handle_note.join()

        handle_theme.join()
        
        logger.info(record_detail(target, f"完成",f"一共{usage_time(start_time)}"))



if __name__ == '__main__':
    lst=["补气血吃什么","黄芪","淮山药","麦冬","祛湿"]
    app=App()
    app.run(lst,search_count=50)