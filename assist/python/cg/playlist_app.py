import sys
from queue import Queue
import threading

from pathlib import Path
import os




from base import ThreadTask,get_param_from_url,logger_helper,UpdateTimeType,exception_decorator,except_stack,df_empty,spceial_suffix_files

from playlist_thread import *
from playlist_manager import playlist_manager
from enum import Enum


    
    
    
    
class playlist_app:
    def __init__(self) -> None:

        class_name=self.__class__.__name__
        self.logger=logger_helper(class_name)
        self.manager:playlist_manager=playlist_manager()

        self.url_queue=Queue()
        self.m3u8_queue=Queue()
        self.download_queue=Queue()
        self.merge_queue=Queue()


        self.stop_interact_event=threading.Event()
        m3u8_stop_event=threading.Event()
        download_stop_event=threading.Event()

        self.stop_merge_event=threading.Event()

        self.interact=InteractUrl(self.url_queue,self.m3u8_queue,self.stop_interact_event,m3u8_stop_event)
        self.handle_m3u8=HandleUrl(self.m3u8_queue,self.download_queue,m3u8_stop_event,out_stop_event=download_stop_event)
        self.handle_download=DownloadVideo(self.download_queue,self.merge_queue,download_stop_event,self.stop_merge_event)
        self.handle_merge=MergeVideo(self.merge_queue,self.stop_merge_event)
        pass


            
    @exception_decorator(error_state=False)
    def send_msg(self,urls:list[VideoUrlInfo]|VideoUrlInfo):

        if not urls:
            return
        if isinstance(urls,VideoUrlInfo):
            urls=[urls]
        urls=list(filter(lambda x:x.valid,urls))
        if not urls:
            return
        
        logger=self.logger
        logger.update_target("收到消息",f"url:{urls}")
        logger.trace("开始处理",update_time_type=UpdateTimeType.STAGE)
        for url in urls:
            self.url_queue.put(url)
            logger.trace(f"消息入队",url,update_time_type=UpdateTimeType.STEP)

    
    @exception_decorator(error_state=False)
    def continue_download(self):
        for item in self.manager.undownloaded_lst:
            if not item:
                continue
            self.download_queue.put(item)
    @exception_decorator(error_state=False)
    def continue_handle_url(self):
        msg=self.manager.undownloaded_pure_infos
        if not msg:
            return

        self.send_msg(msg)

    @exception_decorator(error_state=False)
    def continue_merge(self):
        infos=self.manager.undownloaded_pure_infos
        if not infos:
            return

        for info in filter(lambda x: x and x.exist_temp_dir and x.valid ,infos):
            file_paths=spceial_suffix_files(info.temp_dir,[info.suffix],False)
            if not file_paths:
                continue
            self.merge_queue.put((0,file_paths,info.title))

    def save_df(self):
        self.manager.save_xlsx_df()

    def run(self):

        self.interact.start()
        self.handle_m3u8.start()
        self.handle_download.start()
        self.handle_merge.start()
        self.stop_interact_event.set()
        self.url_queue.join()
        self.m3u8_queue.join()
        self.download_queue.join()
        self.merge_queue.join()
        self.interact.join()
        self.handle_m3u8.join()
        self.handle_download.join()
        self.handle_merge.join()


        pass


def main():
    app=playlist_app()

    raw_urls=[
        # VideoUrlInfo(url="http://www.enmoedu.com/nowplay/40158-0-51.html"),
        ]

   
    m3u8_urls=[
        VideoUrlInfo(m3u8_url='https://v1.qrssuv.com/wjv1/202308/19/pWujuxMMY62/video/1000k_720/hls/index.m3u8', title='我的23岁'),

    ]

    # app.send_msg(m3u8_urls) #直接提供m3u8_urlK
    # app.send_msg(raw_urls) #原始url，交互获取m3u8_url

    app.continue_merge() # 继续合并,前提是 已删除 加入的片段
    
    
    # app.continue_handle_url() #继续交互

    # app.continue_download() #继续下载
    
    # app.stop_merge_event.set() #关闭合并功能，手动删除多余片段后，再开启
    
    # app.stop_interact_event.set() #手动添加停止事件，关门手动网页交互功能;也可以直接关闭网页，起到相同效果
    app.run()
    app.save_df()
    pass


if  __name__ == '__main__':


    

    main()