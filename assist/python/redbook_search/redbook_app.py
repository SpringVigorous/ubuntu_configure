#小红书最终版
from queue import Queue
import sys
sys.path.append("..")
sys.path.append(".")

import threading
from DrissionPage._elements.chromium_element import ChromiumElement
from __init__ import *
from base import logger as logger_helper,UpdateTimeType
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
from handle_config import redbook_config
from data import *
from redbook_task import *

from Interact_theme import InteractTheme,ResultType
from Interact_url import InteractUrl



class ThemeApp:
    def __init__(self) :
       pass

    def run(self,themes:list,search_count=20):
       
        app_logger=logger_helper("主题集合","、".join(themes))
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
       
        app_logger=logger_helper("主题集合","、".join(urls))
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
        
        interact=InteractUrl(urls_queue,json_queue,stop_interact_event,stop_parse_event,comment_queue,ResultType.ONLY_NOTE,theme=theme)
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
    # lst=["新图纸来啦！简化版儿童擎天柱头盔图纸"]
    lst=["祛湿"]
    # lst=["补气血吃什么"]
    app=ThemeApp()
    app.run(lst,search_count=30)
    
    
def run_url_app():
    lst= [
    "https://www.xiaohongshu.com/explore/649ab9a800000000120339d8?xsec_token=AB6sqXZF3woHZe4QcuilaoEHkj62ZsAT4YhXz3PchbTNw=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/6643423f000000001e0394c3?xsec_token=ABZmeUeYx3L2TzmZ0w24GX04ZGH8U6FGiocsr3-Ols0PU=&xsec_source=pc_search&source=web_search_result_notes",
    "https://www.xiaohongshu.com/explore/66973c5e000000000d00f7da?xsec_token=ABxQJNbsWV3sEb840f5ZXLB2cIRNpyt549FT4ZoKL92cQ=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/66c1da89000000000503b61e?xsec_token=AB9zK8AnUFz4rtkX8W0Bhw4-6xYeMWSLHC_rETtRNg3sU=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/66515fe30000000005006b82?xsec_token=ABcTmK7JolOsFzzo5vy1zfmFU3kMh0eZ61wLO0aKvaMMs=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/6629ddfb0000000001005f44?xsec_token=ABHNPGvZaA1UxTeN7PrSg5U1LVef_Lf3xmezz4dGR31NQ=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/66224489000000001c007c99?xsec_token=ABMe8iac6ldPXvy363td2Kn7eTEeGi-VpGUv8Y9rtUQjo=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/6709f4900000000016021140?xsec_token=ABFdU7IQ8fCpxsXuEjHZYJmKMHpieAqf2JI1YAUA-NZRQ=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/66ed04f30000000012013949?xsec_token=ABeG6Sh86QMT7_OTU1kFEUu0k99fDuqbw-ZHtZ1PrvIYo=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/661096d9000000001a013d80?xsec_token=ABhp9cv8KkOXjki5iXXxwscbY0wuweYfIcfpU8x84ZuL8=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/66665ce6000000000f00dcc9?xsec_token=ABLGYYgu8skqEzGrGPiurmArz_pW0P4D4OjiM4uTeGiZM=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/66c075ef000000001e01fd24?xsec_token=ABjLRrt9_1dBk4drmY0WTHuhgEO5RN7Rj516yYaNbxs90=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/65d8015c0000000007026167?xsec_token=AB2OgF72EMSe285GvIDIrZAdmtErKVgGpmNTfwqB0DqwQ=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/6672d5bd00000000060078f2?xsec_token=AB5zKGIY_q59X-SrIkLRGC1yca4OsCWRt9wvaCLj6whoY=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/66a0ca35000000000600ecc2?xsec_token=ABo2qZE-B48RL9sOkYI1PBfDMwQvIVZJBH6J5ECERiW50=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/66a49edc000000000600f887?xsec_token=ABgLdozMEWw7FO8EGbUwWfBrWuGgcugiHoJtcRwypPuPg=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/66f3e090000000002a037d0e?xsec_token=ABZ3VOKaYYbI04P_kE-BlShZnDlfx6xuqetMhPg3LKkuk=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/667f558d000000001e0105e4?xsec_token=ABcaORFCs4toC5WX-3JAucBMSYpdZzthN1E_LPJiF7Qeg=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/669e2dce0000000027010112?xsec_token=ABJEiymLYBs9rXnfmY_9FSpI43_EzjEibMvZ7JLzPDRGs=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/66cc096c000000001d0157c9?xsec_token=ABDLMGD5VRuQYQw3MMZWvlrwGliySWVOGYLwk5Zb0NH4k=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/65f2bd8f000000001203f362?xsec_token=ABmtymi81nql7F6feviK-ieGZR55tbiBh0qhb9nFJOz0o=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/667945a3000000001f0053e4?xsec_token=ABbwKEtDoMw9YHhSAFM5MlEKM-c-3XGbLxGWHU7ev8KnQ=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/662cd44d0000000001007e2f?xsec_token=ABu1o7sAHKYYYBtrtGVeoyI-0vSLQzKvgwD-1MoHNIYBc=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/6683aa46000000001c0242a5?xsec_token=ABlUAY5kCf9-tpt-p9oIF9LnrH9oD5CdEYezx3iAlobrg=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/66bb044e00000000250333c7?xsec_token=ABlB2o3YnFFOPt46RAZv8fPuV4CVce8eE-WeTLLsrxeYY=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/6655e532000000001401b0a2?xsec_token=ABJ7Pz9tP4ukH5KJQ2XHgbgcG0QoLrEcy9Sn-YUMIyRyo=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/66e813860000000012010468?xsec_token=AB41Wo6KBc-eoRIOYQfZCORbZSv31a-w7niaGTpIayUbM=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/66797942000000001e01048c?xsec_token=ABbwKEtDoMw9YHhSAFM5MlEPwSOxOHwp_fSS2FJlql08w=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/669a2ca3000000000d00cb4b?xsec_token=ABTWsnFq2Lhsj0YhanglXVxHxBgINSW1pVRetpLOz8jVU=&xsec_source=pc_search&source=web_explore_feed",
    "https://www.xiaohongshu.com/explore/61d56ec40000000021038c55?xsec_token=ABuyY7kY9wElG5Mc5mCEy5zCbzXtKSW9f0QWLf8YA5774=&xsec_source=pc_search&source=web_explore_feed"
    ]
    app=UrlApp()
    app.run("祛湿url",lst)
    
    
    


if __name__ == '__main__':
    # run_theme_app()
    run_url_app()
    
    
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

