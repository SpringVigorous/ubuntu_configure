import sys
from queue import Queue
import threading

from pathlib import Path
import os




from base import ThreadTask,get_param_from_url,logger_helper,UpdateTimeType,exception_decorator,except_stack,df_empty,spceial_suffix_files,envent_sequence,force_merge

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
        self.decode_queue=Queue()
        self.merge_queue=Queue()


        self.stop_interact_event=threading.Event()
        m3u8_stop_event=threading.Event()
        download_stop_event=threading.Event() #停止下载信号

        downloaded_event=threading.Event() #已全部停止下载
        self.decode_stop_event=threading.Event() #停止转换信号
        decoded_event=threading.Event() #已全部停止转换
        
        self.stop_merge_event=envent_sequence()
        self.stop_merge_event.add_envent(downloaded_event)
        self.stop_merge_event.add_envent(decoded_event)

        self.interact=InteractUrl(self.url_queue,self.m3u8_queue,self.stop_interact_event,m3u8_stop_event)
        self.handle_m3u8=HandleUrl(self.m3u8_queue,self.download_queue,m3u8_stop_event,out_stop_event=download_stop_event)
        #解码
        self.handle_decode=DecodeVideo(self.decode_queue,self.merge_queue,self.decode_stop_event,decoded_event)       
        self.handle_download=DownloadVideo(self.download_queue,self.merge_queue,download_stop_event,downloaded_event)
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
        logger.update_target("收到消息",f"共{len(urls)}条")
        logger.trace("开始处理",update_time_type=UpdateTimeType.STAGE)
        for index,url in enumerate( urls):
            self.url_queue.put(url)
            logger.trace(f"消息入队",f"第{index+1}条：/n【{url}】",update_time_type=UpdateTimeType.STEP)

    
    @exception_decorator(error_state=False)
    def continue_download(self):
        
        lst=self.manager.undownloaded_lst
        if not lst:
            return
        
        for item in lst:
            if not item:
                continue
            self.download_queue.put(item)
            
    @exception_decorator(error_state=False)
    def continue_decode(self):
        
        lst=self.manager.undownloaded_decode_lst
        if not lst:
            return
        for item in lst:
            if not item:
                continue
            self.decode_queue.put(item)
            
            
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
        self.handle_decode.start()
        
        self.stop_interact_event.set()
        
        #关闭 解码信号
        self.decode_stop_event.set()
       
        self.decode_queue.join()
        self.url_queue.join()
        self.m3u8_queue.join()
        self.download_queue.join()
        self.merge_queue.join()
        
        
        self.handle_decode.join()
        self.interact.join()
        self.handle_m3u8.join()
        self.handle_download.join()
        self.handle_merge.join()


        pass





def main():
    app=playlist_app()

    raw_urls=[
        # VideoUrlInfo(url="http://www.yingliyt.com/vod/play/394720-1-1.html"),
        # VideoUrlInfo(url="https://www.wixin.vip/xin/116717.html"),
        VideoUrlInfo(url="https://yenchuang.com/d/63889/68464604789fc.html"),
        ]

   
    m3u8_urls=[


VideoUrlInfo(m3u8_url='https://cdn.yddsha2.com/m3u87/share/1481145/1650779/20240524/050607/360/master.m3u8?sign=0bc20ad293f5d0e3a28be11fdfcf354d&t=1765702378', title='昆虫总动员2-来自远方的后援军'),
VideoUrlInfo(m3u8_url='https://s.xlzys.com/play/RdGOzLdD/index.m3u8', title='昆虫总动员'),

    ]

    # app.send_msg(m3u8_urls) #直接提供m3u8_url
    app.send_msg(raw_urls) #原始url，交互获取m3u8_url

    # app.continue_decode() # 继续解码,前提是确保编码未处理
    
    # app.continue_merge() # 继续合并,前提是 已删除 加入的片段
    
    
    # app.continue_handle_url() #继续交互

    # app.continue_download() #继续下载
    
    # app.stop_merge_event.set() #关闭合并功能，手动删除多余片段后，再开启
    
    # app.stop_interact_event.set() #手动添加停止事件，关门手动网页交互功能;也可以直接关闭网页，起到相同效果
    
    app.run()
    app.save_df()
    pass

def forece_merge_test():
    
    from base import kid_root
    force_merge(kid_root\r"拼音练习\1",kid_root\r"拼音练习\07_zhchshr_王诗玥.mp4",[".mp4"])

if  __name__ == '__main__':
    
    
    # forece_merge_test()
    # exit()
    
    main()