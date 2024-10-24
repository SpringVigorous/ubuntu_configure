#小红书最终版
from queue import Queue,Empty
import sys
sys.path.append("..")
sys.path.append(".")


import threading
import time
from DrissionPage import WebPage
from DrissionPage.common import Actions,Keys
from DrissionPage._elements.chromium_element import ChromiumElement
# from DrissionPage._configs.chromium_options import ChromiumOptions

import concurrent.futures

from __init__ import *
from base.com_log import logger as logger,usage_time,logger_helper,UpdateTimeType

from base.string_tools import sanitize_filename,datetime_flag


from HmTask.redbook_tools import *

from docx import Document
from docx.enum.style import WD_STYLE_TYPE

import pandas as pd
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor , wait, ALL_COMPLETED
from collections import namedtuple
import json
from handle_comment import NoteWriter
from base.except_tools import except_stack
from base.com_decorator import exception_decorator
from base.state import ReturnState
import re
from base import ThreadTask
# from base.task.thread_task import ThreadTask



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

note_type_map={"all":'xpath://div[@id="note"]',
            "normal":'xpath://div[@id="short_note"]',
            "video":'xpath://div[@id="video_note"]',
            }


search_input_path ='xpath://input[@class="search-input"]'
search_button_path='xpath://div[@class="search-icon"]'
close_path='xpath://div[@class="close close-mask-dark"]'

#用户

user_path='xpath://div[@id="user"]'

user_item='xpath://div[@class="user-item-box"]'            

user_notes='xpath://section[@class="note-item"]'
#悬停
filter_box=  'xpath://div[@class="filter-box"]'  
    
filter_path='xpath://svg[@class="reds-icon filter-icon"]'


note_scroll_path='xpath://div[@class="note-scroller"]'

comments_container_path='xpath://div[@class="comments-container"]'
comment_content_path='xpath://div[@class="content"]'
comment_list_path='xpath:/div[@class="list-container" and @name="list]'
comment_end_path='xpath://div[@class="end-container"]'
comment_more_path='xpath://div[@class="show-more"]'



scroll_to_view_js="arguments[0].scrollIntoView();"


listen_search='web/v1/search/notes'
listen_note="api/sns/web/v1/feed"
listen_comment="api/sns/web/v2/comment/page"

#同步输出
sync_note_comment=False


flag_suffix=" - 小红书"
@exception_decorator()
def click_more_info(more_info):
    if more_info:
        more_info.click()
    # comment_logger.trace("more-click", f"第{index}次", update_time_type=UpdateTimeType.STEP)

def handle_more(show_mores,comment_logger):
    if not show_mores:
        return
    if len(show_mores)<2:
        click_more_info(more_info=show_mores[0])
        return
        
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        
        # 使用 enumerate 获取索引和元素
        futures = [executor.submit(click_more_info, more_info) for  more_info in show_mores]
        
        # 等待所有任务完成
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()  # 获取结果或处理异常
            except Exception as e:
                comment_logger.error("异常",except_stack(),update_time_type=True)

def net_exception(title:str)->bool:
        # 定义关键词列表
        keywords = ["网络", "连接", "超时", "错误", "异常", "失败"]
        
        # 构建正则表达式模式
        pattern = "|".join(keywords)
        
        # 使用正则表达式搜索
        return re.search(pattern, title)
    
    
    
class Interact(ThreadTask):
    def __init__(self, root_dir:str=setting.redbook_notes_dir,search_count:int=10):
        super().__init__(global_theme_queue,output_queue=None,stop_event=stop_interact_event)
        # chrome_options = Options()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')


        self.wp=WebPage()
        self.root_dir=root_dir
        self.search_count=search_count
        url='https://www.xiaohongshu.com/'
        
        self.wp.get(url)


        self.theme_logger=logger_helper("采集")

        
    def _except_to_break(self)->bool:
        return False
    
   
    def _final_run_after(self):
        stop_parse_event.set()
        pass
    
    def close_note(self):
        self.wp.wait.eles_loaded(close_path)
        close_flag=self.wp.ele(close_path)
        if close_flag:
            try:
                close_flag.click()
                time.sleep(.5)
            except:
                self.show_except_stack()

    
    def show_except_stack(self):
        self.theme_logger.error("异常",except_stack(),update_time_type=True)
    
    def urls(self,theme):

        #测试部分——————————————————————————————————————————————————
        urls_path=os.path.join(self.theme_dir,f"{theme}_urls.json")
        if os.path.exists(urls_path):
            with open(urls_path,"r",encoding="utf-8-sig") as f:
                return json.load(f) 
        #测试部分——————————————————————————————————————————————————

        self.theme_logger.update_target("采集url",theme)
        self.theme_logger.reset_time()
        self.theme_logger.info("开始")
        hrefs=[]
        try:

            #搜索输入框
            if not self.wp.wait.ele_displayed(search_input_path):
                return
            search_input = self.wp.ele(search_input_path)
            search_input.clear()
            search_input.input(f'{theme}\n')
            # time.sleep(.4)

            #搜索按钮
            if not self.wp.wait.ele_displayed(search_button_path):
                return
            seach_button=self.wp.ele(search_button_path)
            if not seach_button:
                sys.exit(0)
            self.wp.ele(search_button_path).click()


            
            type_button=self.wp.ele(note_type_map["all"])
            if type_button:
                type_button.click()
            self.wp.ele(search_button_path).click() #再次搜索下
            time.sleep(.5)

            while len(hrefs)<self.search_count:
                secManager=SectionManager(self.wp)
                secManager.update()
                time.sleep(.5)
                for item in secManager.urls:
                    if item not in hrefs:
                        hrefs.append(item)
                sec=secManager.last
                sec.click()
                self.close_note()

        except Exception as e:
            self.show_except_stack()
            
        #测试部分——————————————————————————————————————————————————
        with open(urls_path,"w",encoding="utf-8-sig") as f:
            json.dump(hrefs,f,ensure_ascii=False)  
        #测试部分——————————————————————————————————————————————————
  
        return hrefs
    
    
    def handle_comment_by_urls(self,urls,csvj_writer:NoteWriter):
        
        self.theme_logger.update_target("采集评论—主题")
        self.theme_logger.reset_time()
        self.theme_logger.info("开始")
        for url in urls:
            self.wp.get(url)
            # time.sleep(.3)
            result=ReturnState.from_state(self.handle_comment(csvj_writer))
            if result.is_except:
                return ReturnState.EXCEPT
        self.theme_logger.info("完成",update_time_type=UpdateTimeType.ALL)
        
        
    @property
    def title(self)->str:
        return self.wp.title.replace(flag_suffix,"")
        
    
    @exception_decorator() 
    def handle_comment(self,csvj_writer:NoteWriter,note_id:str=""):
       
        time.sleep(.5)
        #处理评论
        title=self.title
        comment_logger=logger_helper("采集评论",title)
        
        container=self.wp.ele(comments_container_path,timeout=1)
        comments_total=0
        try:
            raw_total=container.ele('.total').text
            splits=raw_total.split()
            if len(splits)>1:
                comments_total=int( splits[1])
        except:
            #网络问题，提前退出
            if net_exception(title):
                return ReturnState.EXCEPT
            pass

        comment_logger.info("开始",f"总共{comments_total}个",update_time_type=UpdateTimeType.STEP)
        if comments_total<1:
            comment_logger.info("结束",f"共计时长",update_time_type=UpdateTimeType.ALL)
            return
        
        scroll_count=0
        while not self.wp.wait.ele_displayed(comment_end_path,timeout=.1):
            #滚动
            if not self.wp.wait.ele_displayed(note_scroll_path,timeout=.5):
                break
            scroller= self.wp.ele(note_scroll_path)
            scroller.scroll.to_bottom()
            # time.sleep(.1)
            scroll_count+=1
        comment_logger.info("滚动到底",f"共{scroll_count}次",update_time_type=UpdateTimeType.STEP)
               

        more_index=1

        while True:        
            #更多评论
            show_mores=self.wp.eles(comment_more_path,timeout=1)
            comment_logger.trace("show-more",f"第{more_index}次,共{len(show_mores)}个",update_time_type=UpdateTimeType.STEP)
            if not show_mores:
                break
            handle_more(show_mores,comment_logger)
            comment_logger.trace("more-click",f"共{len(show_mores)}个,完成",update_time_type=UpdateTimeType.STEP)
            more_index+=1


            
        comment_container=self.wp.ele(comments_container_path,timeout=.5)
        if not comment_container:
            return
        comment_container_html=comment_container.html
        
        comment_logger.info("结束",f"共计时长",update_time_type=UpdateTimeType.ALL)

        with open(f"{self.theme_dir}/{title}.html","w",encoding="utf-8-sig") as f:
            f.write(comment_container_html)
        csvj_writer.handle_comment(comment_container_html,note_id=note_id,note_title=title)

    #第一步，需要调用这个
    @exception_decorator()
    def seach_theme(self,theme):

        self.theme_logger.update_target("采集主题",theme)
        self.theme_logger.reset_time()
        self.theme_logger.info("开始")

        #搜索输入框
        if not self.wp.wait.ele_displayed(search_input_path):
            return False
        search_input = self.wp.ele(search_input_path)
        search_input.clear()
        search_input.input(f'{theme}\n')
        # time.sleep(.4)

        #搜索按钮
        if not self.wp.wait.ele_displayed(search_button_path):
            return False
        seach_button=self.wp.ele(search_button_path)
        if not seach_button:
            sys.exit(0)
        self.wp.ele(search_button_path).click()

        type_button=self.wp.ele(note_type_map["all"])
        if type_button:
            type_button.click()
        self.wp.ele(search_button_path).click() #再次搜索下
        
        return True


    def handle_theme(self,theme,csvj_writer):

        if not self.seach_theme(theme):
            return False
        hrefs=[]
        try:

            time.sleep(.5)
            self.wp.listen.start(listen_note) 

            secManager=SectionManager(self.wp)
            secManager.update()
            generator=secManager.next()
            while len(hrefs)<self.search_count:
                sec_item=next(generator)
                sec=sec_item.sec if sec_item else None
                if not sec :
                    #更新表格
                    secManager.set_wp(self.wp)
                    secManager.update()
                    continue
                time.sleep(.5)
                
                try:
                    if(self.wp.wait.ele_displayed(sec,timeout=1)):
                        sec.click()
                    else:
                        continue
                except:
                    secManager.resume_cur()
                    secManager.update()
                    continue  
                            
                body=None
                while True:
                    item=self.wp.listen.wait()
                    body=item.response.body
                    if not body:
                        continue
                    if item.target==listen_note:
                        break
                
                body["my_link"]=self.wp.url
                body=JsonData(theme=self.theme,json_data=body)
                global_json_queue.put(body)    #整理到内部队列
                note_id=""
                try:
                    note_id=body[1]['data']['items'][0]['id']

                except:
                    pass
                
                #获取url
                hrefs.append(sec_item.url)
                if sync_note_comment:
                    self.handle_comment(csvj_writer,note_id=note_id)
                self.close_note()
                time.sleep(.5)
                
        
        except Exception as e:
            self.theme_logger.error("异常",except_stack(),update_time_type=True)
            pass
        finally:
            self.theme_logger.info("完成",f"一共获取{len(hrefs)}个",update_time_type=UpdateTimeType.ALL)
            return hrefs
        
        
        
    @exception_decorator()
    def _handle_data(self, theme):
        self.theme=theme

        self.theme_dir=os.path.join(self.root_dir, theme)
        os.makedirs(self.theme_dir, exist_ok=True)

        csvj_writer=NoteWriter(os.path.join( self.theme_dir,f"评论-{theme}.csv"))
        hrefs=self.handle_theme(theme,csvj_writer)
        if not sync_note_comment and hrefs:
            #下列只是针对 评论部分
            # self.handle_urls(self.urls(theme),csvj_writer)
            self.handle_comment_by_urls(hrefs,csvj_writer)
        return 

      
#主要用于写入临时文件，队列信息为（file_path,content,mode,encoding）
class WriteFile(ThreadTask):
    def __init__(self):
        super().__init__(input_queue=global_raw_data_queue, stop_event=stop_hanle_event)
        
    def _handle_data(self, file_info):
        file_path,content=file_info
        read_write_sync(content,file_path,mode="w",encoding="utf-8-sig")
        


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
    
redbook_dir=r"F:/worm_practice/red_book"
redbook_history_dir=f"{redbook_dir}/history"
redbook_notes_dir=f"{redbook_dir}/notes"
redbook_cache_dir=f"{redbook_notes_dir}/notes"

class Parse(ThreadTask,NoteDir):
    def __init__(self, dest_dir=setting.redbook_notes_dir):
        super().__init__(input_queue=global_json_queue, output_queue=global_note_queue, stop_event=stop_parse_event)
        NoteDir.__init__(self,dest_dir=dest_dir)
        self.datas_queue=global_notes_queue
        self.datas_lst:list[NoteInfo]=[] #同一个主题
        self.output_file_queue=global_raw_data_queue

        self.cur_theme=""
        self.themes_data:list[NotesData]=[] #多个主题
        


    def _final_run_after(self):
        start_time=time.time()
        #Excle输出
        outPath = os.path.join(self.CurPath,f"{datetime_flag()}.xlsx")

        parse_logger=logger_helper("汇总excle文件",outPath)
        parse_logger.trace("开始")
        self.handle_theme()
        stop_hanle_event.set()

        with pd.ExcelWriter(outPath) as writer:
            for info in self.themes_data:
                if not info.pd is None:
                    info.pd.to_excel(writer, sheet_name=info.theme)
        parse_logger.trace("写入成功",update_time_type=UpdateTimeType.ALL)
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
        
        
    
    
    def _handle_data(self, data:JsonData):

        theme,raw_data=data.theme,data.json_data
        if not self.cur_theme:
            self.cur_theme=theme
        elif self.cur_theme != theme:  #切换主题
            self.handle_theme()
            self.cur_theme=theme
            pass    
        
        link=raw_data.get("my_link","")
        web_title=raw_data.get("title","")
        
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



class HandleNote(InputTask):
    def __init__(self, dest_dir=setting.redbook_notes_dir):
        super().__init__(input_queue=global_note_queue, stop_event=stop_hanle_event,dest_dir=dest_dir)
    def _handle_data(self, noteinfo:NoteInfo):
        
        asyncio.run(noteinfo.handle_note())
        
#以下两个可以并行
class HandleTheme(InputTask):
    def __init__(self, dest_dir=setting.redbook_notes_dir):
        super().__init__(input_queue=global_notes_queue, stop_event=stop_hanle_event,dest_dir=dest_dir)

    def _final_run_after(self):
        pass
        
    def _handle_data(self, theme_pds):
        theme,df=theme_pds.theme,theme_pds.pd
        #临时数据，缓存使用、
        dict_data=df.to_dict("records")
        to_theme_word(theme_name=theme,root_dir=self.CurPath,dict_data=dict_data)





class App:
    def __init__(self) :
       pass

    def run(self,themes:list,search_count=20):

        
        app_logger=logger_helper("主题集合","、".join(themes))
        app_logger.info("开始")

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


        handle_note.join()

        handle_theme.join()
        
        app_logger.info("完成",update_time_type=UpdateTimeType.ALL)



if __name__ == '__main__':
    # lst=["补气血吃什么","黄芪","淮山药","麦冬","祛湿","健脾养胃"]
    # lst=["新图纸来啦！简化版儿童擎天柱头盔图纸"]
    # lst=["祛湿"]
    lst=["补气血吃什么"]
    app=App()
    app.run(lst,search_count=5)