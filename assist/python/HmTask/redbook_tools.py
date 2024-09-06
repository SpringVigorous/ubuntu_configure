﻿
import datetime
import pandas as pd
from pathlib import Path

from docx import Document,opc,oxml
from docx.shared import Inches,Cm,Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import sys
sys.path.append("..")
sys.path.append(".")

from __init__ import *
from uuid import uuid4
from PIL import Image
import os
import time
import json
from base.file_tools import read_write_async,read_write_sync,download_async,download_sync

from base.path_tools import normal_path
from __init__ import *
from base.com_log import logger as logger
from base import setting as setting
from base.string_tools import sanitize_filename
from docx.enum.style import WD_STYLE_TYPE

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


def convert_image_to_jpg(image_path,dest_path=None):
    if not dest_path:
        dest_path=image_path
    info =f"{image_path},{image_path}->{dest_path}"
    if not os.path.exists(image_path):
        logger.error(f"图片文件不存在:{info}失败")
        return
    # 打开图片
    image = Image.open(image_path).convert('RGB')
    # 保存为 JPEG 格式


    image.save(dest_path, 'JPEG')
    if os.path.exists(dest_path):
        os.remove(image_path)
    
        return
    # 打开图片
    image = Image.open(image_path).convert('RGB')
    # 保存为 JPEG 格式
    if not dest_path:
        dest_path=image_path

    image.save(dest_path, 'JPEG')
    logger.trace(f"图片类型转换成功：{info}")

def add_hyperlink(paragraph, url, text, color=None):
    # 获取文档部分
    part = paragraph.part
    
    # 创建超链接关系
    r_id = part.relate_to(url, opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
    
    # 创建超链接元素
    hyperlink = oxml.shared.OxmlElement('w:hyperlink')
    hyperlink.set(oxml.shared.qn('r:id'), r_id)
    
    # 创建新的运行元素
    new_run = oxml.shared.OxmlElement('w:r')
    rPr = oxml.shared.OxmlElement('w:rPr')
    
    # 设置颜色
    if color:
        c = oxml.shared.OxmlElement('w:color')
        c.set(oxml.shared.qn('w:val'), color)
        rPr.append(c)
    new_run.append(rPr)
    new_run.text = text
    hyperlink.append(new_run)

    r = paragraph._p.add_r()
    r.append(hyperlink)

    return hyperlink
        
        
        


def wait_for_file_exist(file_path, timeout=5):
    start_time = time.time()
    cur_path = normal_path(file_path)
    while time.time() - start_time < timeout:
        if os.path.exists(cur_path):
            logger.debug(f"等待{time.time()-start_time}秒后，文件 {cur_path} 存在")
            return True
        time.sleep(0.5)  # 每0.5秒检查一次
    
    logger.error(f"等待 {timeout} 秒后，文件 {cur_path} 仍然不存在")
    return False

class NoteInfo:
    #CountIndex=0
    def __init__(self,title,content,create_time,update_time,image_urls,author,thumbs,
                 collected,shared,comment,note_id,current_time,video_urls,image_lst=[],
                 video_lst=[],note_path="",type="note",link=""):
        self.title=title
        self.content=content
        self.create_time=create_time    
        self.update_time=update_time  
        self.image_urls=image_urls if isinstance(image_urls,list) else json.loads(image_urls)
        self.video_urls=video_urls if isinstance(video_urls,list) else json.loads(video_urls)
        
        self.author=author
        self.thumbs=thumbs
        self.collected=collected
        self.shared=shared
        self.comment=comment
        self.note_id=note_id
        self.current_time=current_time

        self.image_lst=image_lst if isinstance(image_lst,list) else json.loads(image_lst)
        self.video_lst=video_lst if isinstance(video_lst,list) else json.loads(video_lst)

        self.note_path=note_path
        self.type=type if type else ""
        self.link=link if link else ""
        
    def __str__(self) -> str:

        contents=[]
        if self.has_title:
            contents.append(f"title:{self.title}")
        if self.has_link:
            contents.append(f"link:{self.link}")
        if self.has_type:
            contents.append(f"type:{self.type}")
        
        if self.has_note_id:
            contents.append(f"note_id:{self.note_id}")
        if self.has_current_time:
            contents.append(f"current_time:{self.current_time}")
        if self.has_create_time:
            contents.append(f"create_time:{self.create_time}")
        if self.has_update_time:
            contents.append(f"update_time:{self.update_time}")
        if self.has_images:
            contents.append(f"image_urls:{"\n".join(self.image_urls)}")
        if self.has_video:
            contents.append(f"video_urls:{"\n".join(self.video_urls)}")
        if self.has_author:
            contents.append(f"author:{self.author}")
        if self.has_thumbs:
            contents.append(f"thumbs:{self.thumbs}")
        if self.has_collected:
            contents.append(f"collected:{self.collected}")
        if self.has_shared:
            contents.append(f"shared:{self.shared}")
        if self.has_comment:
            contents.append(f"comment:{self.comment}")
        if self.has_content:
            contents.append(f"content:{self.content}")
        
        if self.has_image_lst:
            contents.append(f"image_lst:{"\n".join(self.image_lst)}")
        if self.has_video_lst:
            contents.append(f"video_lst:{"\n".join(self.video_lst)}")
        
        return '\n'.join(contents)+"\n"


    @property
    def has_title(self)->bool:
        return self.title
    @property
    def has_images(self)->bool:
        return self.image_urls
    
    @property
    def has_video(self)->bool:
        return self.video_urls
    
    @property
    def has_content(self)->bool:
        return self.content
    
    @property
    def has_author(self)->bool:
        return self.author
    
    @property
    def has_thumbs(self)->bool:
        return self.thumbs
    
    @property
    def has_collected(self)->bool:
        return self.collected
    
    @property
    def has_shared(self)->bool:
        return self.shared
    
    @property
    def has_comment(self)->bool:
        return self.comment
    
    @property
    def has_note_id(self)->bool:
        return self.note_id
    
    @property
    def has_create_time(self)->bool:
        return self.create_time
    
    @property
    def has_update_time(self)->bool:
        return self.update_time
    
    @property
    def has_current_time(self)->bool:
        return self.current_time
    
    @property
    def has_image_lst(self)->bool:
        return self.image_lst
    @property
    def has_video_lst(self)->bool:
        return self.video_lst
    
    @property
    def has_type(self)->bool:
        return self.type
    @property
    def has_link(self)->bool:
        return self.link
    def set_root_dir(self,root_dir,cur_index:int =-1):


        sub_dir=f"{cur_index}_{self.title}" if cur_index>0 else self.title

        cur_dir=os.path.join(root_dir,sub_dir)

        dest_image_dir=os.path.join(cur_dir,"images/")
        dest_video_dir=os.path.join(cur_dir,"videos/")
        self.note_path=os.path.join(cur_dir,  f"{self.title}.txt")

        os.makedirs(os.path.dirname(dest_image_dir),exist_ok=True)
        os.makedirs(os.path.dirname(dest_video_dir),exist_ok=True)

        self.image_lst=[normal_path(os.path.join(dest_image_dir,f"{i+1}.jpg")) for i in range(len(self.image_urls))]
        self.video_lst=[normal_path(os.path.join(dest_video_dir,f"{i+1}.mp4")) for i in range(len(self.video_urls))] 
        
        
    #下载图片及视频
    def download(self):
        urls=self.image_urls+self.video_urls
        
        #查找前缀
        suffix=".xxyy"
        if self.image_urls:
            url=self.image_urls[0]
            parts=url.split("_")
            if len(parts)>2:
                suffix=parts[-2]
        
        image_lst=[Path(file_path).with_suffix("."+suffix)  for file_path in self.image_lst]
        
        dests=image_lst+self.video_lst
        #图片 + 视频
        for url,dest in zip(urls,dests):
            download_sync(url,dest) 
        if suffix in ["jpg","jpeg"]:
            return
        for file_path,dest_path in zip(image_lst,self.image_lst):
            convert_image_to_jpg(file_path,dest_path)
          
    #文本
    def write_to_notepad(self):
        read_write_sync(str(self),self.note_path,mode="w",encoding="utf-8")
        logger.debug(f"note_path:{self.note_path} 写入成功")

    def write_to_word(self,document:Document):

        heading = document.add_heading(self.title, 2)
        heading.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        



        # 添加表格
        
        def merge_val(ls):
            return ":".join(list(map(str,ls)) )
        
        def merge_vals(ls):
            return " ".join(list(map(merge_val,ls)) )
        
        thumbs=[
        ["点赞",self.thumbs],
        ["收藏",self.collected],
        ["分享",self.shared],
        ]
        
        
        ls=[

            [merge_val(["create",self.create_time]),merge_val(["作者",self.author]),],
            [merge_val(["update",self.update_time]),merge_vals(thumbs),],
            [merge_val(["now",self.current_time]),merge_val(["类型",self.type]),]
        ]
        
        row_count=len(ls)
        #表格
        table = document.add_table(rows=row_count, cols=2)

        for row in range(row_count):
            for cell in range(2):
                table.rows[row].cells[cell].text=ls[row][cell]

        #添加note_id,附带超链接
        id_paragraph = document.add_paragraph()
        id_info=f"id:{self.note_id}"
        #添加链接
        if self.has_link:
            add_hyperlink(id_paragraph, self.link,id_info, color='0563C1')
        else:
            id_paragraph.add_run(id_info)
        
        #图片
        if self.image_lst:
            pic_paragraph = document.add_paragraph()
            pic_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for image_path in self.image_lst:
                cur_path=normal_path(image_path)
                if not (os.path.exists(cur_path) or wait_for_file_exist(cur_path,5)):
                    logger.error(f"image_path:{cur_path} 文件不存在")
                    continue
                
                try:
                    pic_paragraph.add_run().add_picture( cur_path,width=Cm(7))
                except:
                    logger.error(f"image_path:{cur_path} 插入word文档【{self.title}】失败")
                    continue

        
        # if self.video_lst:
        #     video_paragraph = document.add_paragraph().add_run()
        #     for video_path in self.video_lst:
        #         video_paragraph.add_video(video_path,width=Inches(1.5))
        #         video_paragraph.add_run()
            
        
        
        document.add_paragraph(self.content)
        document.add_paragraph('')
        document.add_paragraph('')
        logger.debug(f"word标题:{self.title} 写入成功")
        pass


class Section:
    def __init__(self,sec,yVal,id,already):
        self.sec=sec
        self.yVal=yVal
        self.id=id
        self.already=already

def contain_search_key(str):
    lst=["大家都在搜","相关搜索","热门搜索"]
    return  any([key in str for key in lst])
    

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
        


    def update(self):
        
        # await asyncio.sleep(.3)
        time.sleep(.3)
        
        org_secs=self.wp.eles("xpath://section")
        sorted(org_secs,key=lambda x:x.rect.midpoint[1])

        
        secs=[Section(sec,sec.rect.midpoint[1],sec.raw_text,False)   for sec in org_secs if not contain_search_key(sec.raw_text) ]
        
 
        
        if self.secs:
            for sec in secs:
                
                org=self.get_by_id(sec.id)
                if org:
                    sec.already=org.already
                    
        
        

        self.__set_secs(secs)
    def get_by_id(self ,id):
        secs=[sec for sec in self.secs if sec.id==id]
        return secs[0] if secs else None
        

    
    def next(self):

        for sec in self.cur_secs:
            if not sec.already:
                sec.already=True
                self.cur_index=self.cur_secs.index(sec)
                yield sec.sec
     
    def resume_cur(self):
        if self.cur_index<len(self.cur_secs):
            self.cur_secs[self.cur_index].already=False
        
        
    def count(self):

        return sum([ 0 if sec.already else 1  for sec in self.cur_secs ])
    
def to_theme_word(theme_name,root_dir,dict_data):
        # 创建一个新的文档
    document = Document()
    #整理到word中
    for note_info in dict_data:
        info=NoteInfo(**note_info)
        info.write_to_word(document)
    word_path=os.path.join(root_dir,f"{theme_name}.docx")
    document.save(word_path)
    logger.debug(f"word文档：{word_path} 写入成功")
    


        