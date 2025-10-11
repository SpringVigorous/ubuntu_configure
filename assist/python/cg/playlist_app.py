import sys
from queue import Queue
import threading

from pathlib import Path
import os

root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )
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
        merge_stop_event=threading.Event()


        self.interact=InteractUrl(self.url_queue,self.m3u8_queue,self.stop_interact_event,m3u8_stop_event)
        self.handle_m3u8=HandleUrl(self.m3u8_queue,self.download_queue,m3u8_stop_event,out_stop_event=download_stop_event)
        self.handle_download=DownloadVideo(self.download_queue,self.merge_queue,download_stop_event,merge_stop_event)
        self.handle_merge=MergeVideo(self.merge_queue,merge_stop_event)
        pass


            
    def send_msg(self,urls:list[VideoUrlInfo]|VideoUrlInfo):

        if not urls:
            return
        if isinstance(urls,VideoUrlInfo):
            urls=[urls]
        urls=list(filter(lambda x:x.vaild,urls))
        if not urls:
            return
        
        logger=self.logger
        logger.update_target("收到消息",f"url:{urls}")
        logger.trace("开始处理",update_time_type=UpdateTimeType.STAGE)
        for url in urls:
            self.url_queue.put(url)
            logger.trace(f"消息入队",url,update_time_type=UpdateTimeType.STEP)

    
    def continue_download(self):
        for item in self.manager.undownloaded_lst:
            if not item:
                continue
            self.download_queue.put(item)
    def continue_nom3u8(self):
        lst=self.manager.no_m3u8_url_lst
        if not lst:
            return
        msg=[VideoUrlInfo(url=item) for item in lst]
        self.send_msg(msg)

    def continue_merge(self):
        infos=self.manager.video_infos
        if not infos:
            return

        for info in filter(lambda x:x.exsit_temp_dir and x.vaild ,infos):
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
    # urls.extend([f"http://www.enmoedu.com/nowplay/40158-0-{i}.html" for i in  range(52)])
   
    m3u8_urls=[
        VideoUrlInfo(m3u8_url='https://v.cdnlz19.com/20240327/24474_34f63808/2000k/hls/mixed.m3u8', title='神奇汉字星球_01'),
    ]

    app.send_msg(m3u8_urls) #直接提供m3u8_url
    # app.send_msg(raw_urls) #原始url，交互获取m3u8_url

    # app.continue_merge() # 继续合并,前提是 已删除 加入的片段
    
    
    # app.continue_nom3u8() #继续交互

    # app.continue_download() #继续下载
    
    # app.stop_interact_event.set() #手动添加停止事件，关门手动网页交互功能;也可以直接关闭网页，起到相同效果
    app.run()
    app.save_df()
    pass


if  __name__ == '__main__':
    
    # from base import postfix
    # url="http://vali-ugc.cp31.ott.cibntv.net/65771A2C716357183EE935A69/030002050053C723DB7BA60295BE451E0D0AD3-76D9-C889-45DB-9D352E6E9499.flv.ts?ccode=0502&duration=1756&expire=18000&psid=62bca402ff46c938efda44e76d179f2b41346&ups_client_netip=240exb8fx3155x3600xd0c0x6b07x305fx901d&ups_ts=1760088176&ups_userid=3760073884&apscid=&mnid=&umt=2&type=flv&utid=ArEsIEQEnkgCAWVd%2FGueTwU3&vid=XNzQxNzYyMjA4&t=77e5dd64e2b094c&cug=2&bc=1&si=612&eo=0&ckt=5&m_onoff=0&vkey=Be3cee197bd794640d0fae3222c68a332&fms=c6e28f8767e4553e&tr=1756&le=b9d0651dac07bd659dbb22354fbe2077&app_key=24679788&app_ver=9.5.101&ts_start=0.0&ts_end=9.633&ts_seg_no=0&ts_keyframe=1"
    # print(postfix(url))
    main()