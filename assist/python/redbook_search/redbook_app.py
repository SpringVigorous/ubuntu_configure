#小红书最终版
from queue import Queue
import sys
sys.path.append("..")
sys.path.append(".")

import threading
from DrissionPage._elements.chromium_element import ChromiumElement
from __init__ import *
from base import  logger_helper,UpdateTimeType
from base import setting as setting
from base.string_tools import sanitize_filename,datetime_flag
from redbook_tools import *
from docx import Document
from docx.enum.style import WD_STYLE_TYPE
import pandas as pd
from concurrent.futures import ThreadPoolExecutor , wait, ALL_COMPLETED
import json
import re
from base import ThreadTask

from data import *
from redbook_task import *

from Interact_theme import InteractTheme,ResultType
from Interact_url import InteractUrl



class ThemeApp:
    def __init__(self) :
       pass

    def run(self,themes:list,search_count=20):
       
        app_logger=logger_helper("主题集合","\n"+"\n".join(themes))
        app_logger.info("开始")

        theme_queue= Queue()
        json_queue=Queue() #JsonData or ThemesAllFlag
        raw_data_queue=Queue() #RawData
        note_queue=Queue() #NoteInfo
        notes_queue=Queue() #NotesData
        comment_queue=Queue() #NotesData

        stop_interact_event=threading.Event()
        stop_parse_event=threading.Event()
        stop_hanle_event=threading.Event()
        
        interact=InteractTheme(theme_queue,json_queue,stop_interact_event,stop_parse_event,comment_queue,ResultType.ONLY_NOTE,search_count)
        parse=Parse(json_queue,note_queue,stop_parse_event,stop_hanle_event,out_file_queue=raw_data_queue,datas_queue=notes_queue)
        handle_note=NoteTask(note_queue, stop_hanle_event)
        handle_theme=ThemeTask(notes_queue, stop_hanle_event)
        file_writer=WriteFile(raw_data_queue, stop_hanle_event )
        comment_task= CommentTask(comment_queue,stop_hanle_event)
        
        for theme in themes:
            theme_queue.put(theme)
        
        interact.start()
        parse.start()
        handle_note.start()
        file_writer.start()
        handle_theme.start()
        comment_task.start()
        
        
        stop_interact_event.set()
        interact.join()
        parse.join()
        
        file_writer.join()


        handle_note.join()

        handle_theme.join()
        comment_task.join()
        
        app_logger.info("完成",update_time_type=UpdateTimeType.ALL)



class UrlApp:
    def __init__(self) :
       pass

    def run(self,theme, urls:list):
       
        app_logger=logger_helper("主题集合","\n"+"\n".join(urls))
        app_logger.info("开始")

        urls_queue= Queue()
        json_queue=Queue() #JsonData or ThemesAllFlag
        raw_data_queue=Queue() #RawData
        note_queue=Queue() #NoteInfo
        notes_queue=Queue() #NotesData
        comment_queue=Queue() #NotesData

        stop_interact_event=threading.Event()
        stop_parse_event=threading.Event()
        stop_hanle_event=threading.Event()
        
        interact=InteractUrl(urls_queue,json_queue,stop_interact_event,stop_parse_event,comment_queue,ResultType.ONLY_COMMENT,theme=theme)
        parse=Parse(json_queue,note_queue,stop_parse_event,stop_hanle_event,out_file_queue=raw_data_queue,datas_queue=notes_queue)
        handle_note=NoteTask(note_queue, stop_hanle_event)
        handle_theme=ThemeTask(notes_queue, stop_hanle_event)
        file_writer=WriteFile(raw_data_queue, stop_hanle_event )
        comment_task= CommentTask(comment_queue,stop_hanle_event)
        
        for theme in urls:
            urls_queue.put(theme)
        
        interact.start()
        parse.start()
        handle_note.start()
        file_writer.start()
        handle_theme.start()
        comment_task.start()
        
        
        stop_interact_event.set()
        interact.join()
        parse.join()
        
        file_writer.join()


        handle_note.join()

        handle_theme.join()
        comment_task.join()
        
        app_logger.info("完成",update_time_type=UpdateTimeType.ALL)


def run_theme_app():
    # lst=["补气血吃什么","黄芪","淮山药","麦冬","祛湿","健脾养胃"]
    lst=["静坐","太极拳","站桩","冥想","瑜伽"]
    # lst=["新图纸来啦！简化版儿童擎天柱头盔图纸"]
    # lst=["祛湿"]
    # lst=["补气血吃什么"]
    app=ThemeApp()
    app.run(lst,search_count=30)
    
    
def run_url_app():
    lst= [
    "https://www.xiaohongshu.com/explore/6620b76e00000000040184a8?xsec_token=ABEIAE5mjWxWCLXEBGv3H-tCu6eqDpMh7L1G-2X_-uhMc=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/66f1440c000000001a020443?xsec_token=ABHSqiiGgFPSuzo-SHxeMsri3YSQ4qYCWsWZY1LABuf0A=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/63c9bf6c000000001b0145a9?xsec_token=ABUKX4XcVblxJVzMYShdOBaoSkD4VVE4fTQelhQmCkhA8=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/661df9f4000000001c00a9a6?xsec_token=ABY29zTJEnyDefmL3qwvjFGfBS4MGmEaAXdHn0t9l8YoU=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/672b1301000000001d03817f?xsec_token=ABpCSwihusVbSYFLKMT0yFBvfZz_nTf1xmtcJgdA4dh0Y=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/671a2bcf0000000021007da0?xsec_token=ABjEt9yoskq_2kya_dpBQ6fUj9QVNP-kqQxwFg2upMr4c=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/66497d56000000001401a263?xsec_token=ABPR2Bsd3cUYLoNiGSMUQwHsvJa1vUjs5vWf7E4TQNDCE=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/669e25690000000003025060?xsec_token=ABJEiymLYBs9rXnfmY_9FSpNT6NKJM3uOOiMlIYANbYUk=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/66c5b638000000001d018e5a?xsec_token=ABNPVBAhr_po1_zysMTRkLi1Ac4jtOaQHeYibrs5KEvnM=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/66b96f740000000009017d12?xsec_token=AB1DP9doXmEkAZiMkf84b028Yi9O9j2UfygJxic8ePT4g=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/657aaf9b0000000038021e26?xsec_token=AB1Ct4kgglphQDMcHYLV8FGBepSA-l4nHiLzb_i4z3Ty0=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/6728914b000000001a01fa6c?xsec_token=AB5bOAOPbt-m875qQVmGMFb9ySnzYbiCgxaFs3Xv5gy5g=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/66eebfce000000001e01aacc?xsec_token=AB1OeAzlKiX_NVpkqsNVcn8zKThltMoD4B_iQSjKD2avE=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/67274863000000003c01e144?xsec_token=AB8p7K3MLuHrNj9ov6fA4aXCdEL0_KyVPSDcBG3_wAjKs=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/66164813000000001a013d8a?xsec_token=ABwwcf16nOKu-PsE94HpUyIfftyevjOHnOWaBVcTItPBE=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/66d6d7df000000001f01a648?xsec_token=ABw48FNudLc6hNlyQrsnmz8FBemMIqSF_uDtf69cbA3jg=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/66544ad400000000160121cf?xsec_token=ABjkstG5JL5zJOLf3_lb-WHmI5ETwov-gDps6tnSjEENo=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/6670525b000000000e03317e?xsec_token=ABdvtNqY5JLdwz2BVUfU1VM3SfhTFSn7AYzoga6_wUQZM=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/65bb6770000000002c017ca1?xsec_token=ABIsnZ-_h-6lNeQyQV6sJF2RzDj6OaVCTp9KHFv65wQJU=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/6597d74c000000001d035554?xsec_token=AB3gb0h5qFz0JzmhamQDPVg-eSXNrXk_q2utgYweHs-Ts=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/64cb784e00000000100329d6?xsec_token=AB9LmTS9U5SIPZGhq094_AT0BdF7F-uI9iNt9tQF5uzH4=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/670df7070000000024016e8c?xsec_token=ABG3V4VRRrzh2DtyJBshouf7Otdrvhn5H02ZYnHrPl73A=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/66f127e2000000001b0210ce?xsec_token=ABHSqiiGgFPSuzo-SHxeMsrs6XObsvhfw_U1oIWkwqjtU=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/66cc4074000000001f03d435?xsec_token=ABDLMGD5VRuQYQw3MMZWvlr1iB9hb-qlZTJ3d-nSlmTgA=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/65618642000000001701ee86?xsec_token=ABZzGiOvfu-XLYx9FeIqs1XBxyS6hSnwnch0jwh-JnCeo=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/6707aa46000000001902f9b8?xsec_token=ABcg_7p9SIVZVZQhAj__Fyiupx7PSancoNPmw3kjwbql0=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/65893039000000003403f0b0?xsec_token=AB26cLcdKMJbLaL51K1e-4AMctVhZiK23nw7fEdXN6dRw=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/672a060b000000001b0112c7?xsec_token=ABFMvwEoN0wZIsCZLgw6h8SQblEtbRBn26Bx6YYi3Fs94=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/6702a7c9000000002c02f506?xsec_token=ABXKXEdHHm6edgFtjjU4qIQG03gz3J28uZeX1tMbU4CSA=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/6624d6420000000003023397?xsec_token=ABdayys8cRFgUksnxbKT9-Z9Ay0vkl5ULL2hRvoFVy83g=&xsec_source=pc_search&source=web_explore_feed"
]
    app=UrlApp()
    app.run("补气血吃什么_url",lst)
    
    
    


if __name__ == '__main__':
    run_theme_app()
    # run_url_app()
    
    
    # with open(r'F:\test\ubuntu_configure\assist\python\logs\redbook_app\redbook_app-trace.log', 'r', encoding='utf-8') as f:
    #     log_text = f.read()
    # # 定义正则表达式模式
    # pattern = r'【采集主题】-【开始】详情：(.*?)$'

    # # 使用 re.search 进行匹配
    # # 使用 re.findall 进行匹配，设置 re.MULTILINE 标志以处理多行
    # matches = re.findall(pattern, log_text, re.MULTILINE)

    # # 打印所有匹配的内容
    # for match in matches:
    #     print(match)

