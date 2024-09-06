from queue import Queue,Empty
import sys
sys.path.append("..")
sys.path.append(".")

from base_task import ThreadTask
import threading
import time
from DrissionPage import WebPage


from __init__ import *
from base.com_log import logger as logger
from base import setting as setting
from base.string_tools import sanitize_filename,time_flag


from HmTask.redbook_tools import *

from docx import Document
from docx.enum.style import WD_STYLE_TYPE

import pandas as pd
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor , wait, ALL_COMPLETED
from collections import namedtuple


JsonData=namedtuple("JsonData",["theme","json_data"])
class ThemesAllFlag:
    pass

RawData=namedtuple("RawDataQueue",["file_path","json_data"])
NotesData=namedtuple("NotesData",["theme","pd"])  #pd

ThemesData=namedtuple("ThemesData",["file_path","pds"]) #pds  [notesData]

theme_queue= Queue()
json_queue=Queue() #JsonData or ThemesAllFlag
raw_data_queue=Queue() #RawData
note_queue=Queue() #NoteInfo
notes_queue=Queue() #NotesData
themes_queue=Queue() #ThemesData



stop_parse_event=threading.Event()
stop_hanle_note_event=threading.Event()
stop_file_writer_event=threading.Event()
stop_handle_notes_event=threading.Event()
stop_write_excle_event=threading.Event()









class Interact(threading.Thread):
    def __init__(self, theme_queue:Queue, datas_queue:Queue, data_queue:Queue,root_dir:str=setting.redbook_notes_dir,search_count:int=10,output_file_queue:Queue=None,stop_event=None):
        super().__init__()
        self.theme_queue = theme_queue
        self.datas_queue = datas_queue
        self.data_queue = data_queue
        self.output_file_queue=output_file_queue
        self.wp=WebPage()
        self.root_dir=root_dir
        self.search_count=search_count
        url='https://www.xiaohongshu.com/'
        
        self.wp.get(url)
        self.stop_event=stop_event
        

        time.sleep(5) #初次等待登录
        
    def run(self):
        has_except=False
        
        def clear_queue(q):
            while not q.empty():
                try:
                    val = q.get_nowait()  # 或者使用 q.get(False)
                    q.task_done()
                except Empty:
                    break
                    
        
        
        while not self.theme_queue.empty():
            if has_except:
                clear_queue(self.theme_queue)
                break
            
            start_time=time.time()
            
            theme = self.theme_queue.get()
            theme_info=f"【{theme}】"
            logger.info(f"开始采集{theme_info}……")
            
            json_queue = Queue()
            
            stop_event = threading.Event()
            theme_dir=os.path.join(self.root_dir, theme)
            os.makedirs(theme_dir, exist_ok=True)
            
            parse = Parse(json_queue, output_queue=self.data_queue, datas_queue=self.datas_queue,
                          stop_event=stop_event,dest_dir=theme_dir,output_file_queue=self.output_file_queue)
            parse.start()
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
                        json_queue.put(body)    #整理到内部队列
                        i += 1
                        
                    # if i>3:
                    #     # 测试异常
                    #     raise FileNotFoundError("helllo")
                    #关闭窗口
                    close_flag=self.wp.ele('xpath://div[@class="close close-mask-dark"]')
                    if close_flag:
                        try:
                            close_flag.click()
                        except:
                            continue
            except Exception as e:
                logger.error(f"采集{theme_info}异常【{e}】，共采集{i}个，耗时:{time.time()-start_time:.2f}秒")
                has_except=True
                self.stop_event.set()
            finally:
                stop_event.set()
                self.theme_queue.task_done()
                parse.join()                
                #清空队列，避免等待队列数据
                if has_except:
                    clear_queue(self.theme_queue)
                    break #退出循环，避免后续任务继续执行
                
                logger.info(f"完成采集{theme_info}，共采集{i}个，耗时:{time.time()-start_time:.2f}秒")
                
#主要用于写入临时文件，队列信息为（file_path,content,mode,encoding）
class WriteFile(ThreadTask):
    def __init__(self, input_queue,  stop_event=None):
        super().__init__(input_queue=input_queue, stop_event=stop_event)
        
    def handle_data(self, file_info):
        file_path,content,mode,encoding=file_info
        read_write_sync(content,file_path,mode,encoding)
        
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
    def __init__(self, input_queue, output_queue=None,datas_queue=None, stop_event=None,dest_dir=setting.redbook_notes_dir,output_file_queue=None):
        super().__init__(input_queue, output_queue, stop_event)
        NoteDir.__init__(self,dest_dir=dest_dir)
        self.datas_queue=datas_queue
        self.stop_event=stop_event
        self.datas_lst=[]
        self.output_file_queue=output_file_queue

        
        
    def _each_run_after(self,data):
        if data:
            self.datas_lst.append(data)
    def _final_run_after(self):
        if self.datas_lst:
            df=pd.DataFrame([info.__dict__ for info in self.datas_lst], columns=self.datas_lst[0].__dict__.keys())
            if not df is None:
                df.sort_values(by=["thumbs","create_time"], ascending=[False, True],inplace=True)
            self.datas_queue.put((self.CurPath.name,df) )
        pass
    def handle_data(self, raw_data):
        
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
        
        
        noteinfo.set_root_dir(self.CurPath )
        json_path=os.path.join(self.CurPath,noteinfo.title,f"{noteinfo.title}.json")
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        self.output_file_queue.put((json_path,  json.dumps(raw_data,ensure_ascii=False,indent=4), "w","utf-8-sig") )
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
    def __init__(self, input_queue,  stop_event=None,dest_dir=setting.redbook_notes_dir):
        super().__init__(input_queue=input_queue, stop_event=stop_event,dest_dir=dest_dir)
    def handle_data(self, noteinfo:NoteInfo):
        
        funcs=[noteinfo.write_to_notepad,noteinfo.download]
        threads=[]
        #以下可以并行运行
        with ThreadPoolExecutor(10) as t:
            for func  in funcs:
                future=t.submit(func)
                threads.append(future)
        done, not_done =wait(threads,return_when=ALL_COMPLETED)

#以下两个可以并行
class HandleTheme(InputTask):
    def __init__(self, input_queue,  stop_event=None,dest_dir=setting.redbook_notes_dir):
        super().__init__(input_queue=input_queue, stop_event=stop_event,dest_dir=dest_dir)


        self.dfs=[]
        
    def _final_run_after(self):
        outPath = os.path.join(self.CurPath,f"{time_flag()}.xlsx")
        with pd.ExcelWriter(outPath) as writer:
            for theme,df in self.dfs:
                if not df is None:
                    df.to_excel(writer, sheet_name=theme)
        
    def handle_data(self, theme_pds:tuple):
        theme,df=theme_pds
        #临时数据，缓存使用、
        dict_data=df.to_dict("records")
        to_theme_word(theme_name=theme,root_dir=self.CurPath,dict_data=dict_data)
        self.dfs.append(theme_pds)




class App:
    def __init__(self) :
       pass

    def run(self,themes:list,search_count=20):
        theme_info=f'【{"、".join(themes)}】'
        
        logger.info(f"开始采集{theme_info}……")

        start_time = time.time()
        
        theme_queue=Queue()
        data_queue=Queue()
        datas_queue=Queue()       
        file_queue=Queue()
        
        stop_event=threading.Event()
        root_dir=setting.redbook_notes_dir
        
        interact=Interact(theme_queue=theme_queue,datas_queue=datas_queue,data_queue=data_queue,root_dir=root_dir,search_count=search_count,output_file_queue=file_queue,stop_event=stop_event)
        
        handle_note=HandleNote(input_queue=data_queue,stop_event=stop_event,dest_dir=root_dir)
        handle_theme=HandleTheme(input_queue=datas_queue,stop_event=stop_event,dest_dir=root_dir)
        file_writer=WriteFile(input_queue=file_queue,stop_event=stop_event)
        
        
        for theme in themes:
            theme_queue.put(theme)
        
        interact.start()
        handle_note.start()
        file_writer.start()
        handle_theme.start()
        
        interact.join()
        # stop_event.set()
        
        file_writer.join()
        theme_queue.join()

        handle_note.join()

        handle_theme.join()
        
        logger.info(f"完成采集{theme_info}，一共用时{time.time()- start_time}s")



if __name__ == '__main__':
    lst=["拉筋","指压"]
    app=App()
    app.run(lst,search_count=50)