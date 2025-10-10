import sys
from queue import Queue
import threading

from pathlib import Path
import os

root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )
from base import ThreadTask,get_param_from_url,logger_helper,UpdateTimeType,exception_decorator,except_stack,df_empty

from playlist_thread import *
from playlist_manager import playlist_manager
from enum import Enum

class MessageType(Enum):
    RAW_URL=0,
    M3U8_URL=1
    
    
    
    
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

    def get_queue(self,type:MessageType):
        if type==MessageType.RAW_URL:
            return self.url_queue
        elif type==MessageType.M3U8_URL:
            return self.m3u8_queue
        else:
            return None
    def _send_msg(self,urls:list[tuple|str]|tuple|str,type:MessageType=MessageType.RAW_URL):
        cur_queue=self.get_queue(type)
        if not urls or not cur_queue:
            return
        if isinstance(urls,str):
            urls=[urls]
        logger=self.logger
        logger.update_target("收到消息",f"url:{urls}")
        logger.trace("开始处理",update_time_type=UpdateTimeType.STAGE)
        for url in urls:
            if isinstance(url,tuple):
                
                
                
                cur_queue.put(*url)
            else:
                cur_queue.put(url)
            logger.trace(f"消息入队",url,update_time_type=UpdateTimeType.STEP)
            
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
    def send_raw_url_msg(self,urls:list|str):
        self._send_msg(urls,type=MessageType.RAW_URL)
    
    def send_m3u8_url_msg(self,urls:list[tuple|str]|tuple|str):
        self._send_msg(urls,type=MessageType.M3U8_URL)
    
    def continue_download(self):
        for item in self.manager.undownloaded_lst:
            if not item:
                continue
            self.download_queue.put(item)
    def continue_nom3u8(self):
        lst=self.manager.no_m3u8_lst
        if not lst:
            return
        msg=[VideoUrlInfo(url=item) for item in lst]
        self.send_msg(msg)


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


if  __name__ == '__main__':
    app=playlist_app()

    raw_urls=[
        # VideoUrlInfo(url="http://www.enmoedu.com/nowplay/40158-0-51.html"),
        ]


    # urls.extend([f"http://www.enmoedu.com/nowplay/40158-0-{i}.html" for i in  range(52)])

    
    m3u8_urls=[
        VideoUrlInfo(m3u8_url='https://pl-ali.youku.com/playlist/m3u8?vid=XNzQxNzYyMjA4&type=flv&ups_client_netip=240exb8fx3155x3600xd0c0x6b07x305fx901d&utid=ArEsIEQEnkgCAWVd%2FGueTwU3&ccode=0502&psid=62bca402ff46c938efda44e76d179f2b41346&ups_userid=3760073884&ups_ytid=3760073884&app_ver=9.5.101&duration=1756&expire=18000&drm_type=147&drm_device=7&drm_default=1&nt=1&dyt=1&ups_ts=1760088176&onOff=4656&encr=0&ups_key=187259621ba4fd04e691c0e33135a77f&ckt=5&m_onoff=0&pn=&app_key=24679788&drm_type_value=default&v=v1&bkp=0', title='LoveEnglish_01'),

    ]

    app.send_msg(m3u8_urls)
    # app.send_msg(raw_urls)
    app.continue_nom3u8()
    app.continue_download()
    #停止
    # app.stop_interact_event.set()
    app.run()
    app.save_df()