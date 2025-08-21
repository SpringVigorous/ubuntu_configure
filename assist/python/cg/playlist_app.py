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

    def send_msg(self,urls:list|str):
        if not urls:return
        if isinstance(urls,str):
            urls=[urls]
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
        for item in self.manager.nom3u8_lst:
            if not item:
                continue
            self.url_queue.put(item)


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

    urls=[]
    # urls.extend([
    #     "https://00two.com/vodplay/nazhazhimotongnaohai-1-1.html",
    # ])

    # urls.extend([f"https://www.588806.com/vodplay/142207-0-{i}.html" for i in  range(81)])


    app.send_msg(urls)
    # app.continue_nom3u8()
    # app.continue_download()
    app.run()
    app.save_df()