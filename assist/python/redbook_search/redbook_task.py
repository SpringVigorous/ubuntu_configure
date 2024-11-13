import time
import os
from pathlib import Path
from base import ThreadTask
from handle_config import redbook_config
from base.except_tools import except_stack
from base.com_decorator import exception_decorator
from base.state import ReturnState
from base import logger as logger_helper,UpdateTimeType
from base import read_write_sync, datetime_flag,sanitize_filename



from data import *
from redbook_tools import *
from redbook_path import *
    
#主要用于写入临时文件，队列信息为（file_path,content,mode,encoding）
class WriteFile(ThreadTask):
    def __init__(self,input_queue, stop_event):
        super().__init__(input_queue=input_queue, stop_event=stop_event)
        self.task_logger.update_target("写入临时文件")
        
    def _handle_data(self, file_info):
        file_path,content=file_info
        read_write_sync(content,file_path,mode="w",encoding="utf-8-sig")
        


class NoteDir:
    def __init__(self,dest_dir:str=redbook_config.setting.note_path):
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
    def __init__(self, input_queue,output_queue,stop_event,out_stop_event,out_file_queue,datas_queue):
        super().__init__(input_queue=input_queue, output_queue=output_queue, stop_event=stop_event,out_stop_event=out_stop_event)
        NoteDir.__init__(self,dest_dir=redbook_config.setting.note_path)
        self.datas_queue=datas_queue
        self.datas_lst:list[NoteInfo]=[] #同一个主题
        self.output_file_queue=out_file_queue

        self.cur_theme=""
        self.themes_data:list[NotesData]=[] #多个主题
        self.task_logger.update_target("解析json包")


    def _final_run_after(self):

        #Excle输出
        outPath = os.path.join(self.CurPath,f"{datetime_flag()}.xlsx")

        parse_logger=logger_helper("汇总excle文件",outPath)
        parse_logger.trace("开始")
        self.handle_theme()


        with pd.ExcelWriter(outPath) as writer:
            for info in self.themes_data:
                if not info.pd is None:
                    info.pd.to_excel(writer, sheet_name=info.theme)
                    parse_logger.trace("成功",f"写入表单：{info.theme}",update_time_type=UpdateTimeType.STEP)
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
            title=note_id if not web_title else sanitize_filename(web_title)#str(uuid4())
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
    def __init__(self, input_queue,  stop_event=None,dest_dir=redbook_config.setting.note_path):
        super().__init__(input_queue=input_queue, stop_event=stop_event)
        NoteDir.__init__(self,dest_dir=dest_dir)


class CommentTask(InputTask):
    def __init__(self,input_queue,stop_event):
        super().__init__(input_queue=input_queue, stop_event=stop_event,dest_dir=redbook_config.setting.note_path)
        self.task_logger.update_target("处理评论")
        
        
    def _handle_data(self, info:CommentData):
        csvj_writer,theme,comment_container_html,note_id,note_title=info.writer,info.theme,info.html,info.note_id,info.note_title
        
        # title_filename= sanitize_filename(note_title)
        
        # cache_html_path= comment_html_cache_path(self.dest_dir, theme,title_filename)
        # os.makedirs(os.path.dirname(cache_html_path), exist_ok=True)
        self.task_logger.update_target("",f"{self.input_count}\t {note_title}")
        self.task_logger.update_step()
        self.task_logger.trace("开始")    
        # with open(cache_html_path,"a",encoding="utf-8-sig") as f:
        #     f.write(comment_container_html)
        # self.task_logger.trace("写入缓存文件",cache_html_path,update_time_type=UpdateTimeType.STEP)    
        
        csvj_writer.handle_comment(comment_container_html,note_id=note_id,note_title=note_title)
        self.task_logger.trace("成功","添加入记录表格",update_time_type=UpdateTimeType.STEP)    


class NoteTask(InputTask):
    def __init__(self,input_queue,stop_event):
        super().__init__(input_queue=input_queue, stop_event=stop_event,dest_dir=redbook_config.setting.note_path)
        self.task_logger.update_target("处理单个笔记内容")
    def _handle_data(self, noteinfo:NoteInfo):
        
        asyncio.run(noteinfo.handle_note())
        
#以下两个可以并行
class ThemeTask(InputTask):
    def __init__(self,input_queue,stop_event):
        super().__init__(input_queue=input_queue, stop_event=stop_event,dest_dir=redbook_config.setting.note_path)
        self.task_logger.update_target("处理主题内容")

        
    def _handle_data(self, theme_pds):
        theme,df=theme_pds.theme,theme_pds.pd
        #临时数据，缓存使用、
        dict_data=df.to_dict("records")
        to_theme_word(theme_name=theme,root_dir=self.CurPath,dict_data=dict_data)

