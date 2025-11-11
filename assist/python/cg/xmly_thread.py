from xmly_mp3 import *
import pandas as pd

from DrissionPage import WebPage
from selenium.webdriver.common.by import By

from base import logger_helper,exception_decorator,write_to_bin,UpdateTimeType,ThreadTask
from pathlib import Path
import os
from queue import Queue
import threading

class InteractUrl(ThreadTask):
    
    def __init__(self,input_queue,stop_envent) -> None:
        super().__init__(input_queue,output_queue=None,stop_event=stop_envent,out_stop_event=None)
        self._wp:WebPage=None
        # self._logger=logger_helper(self.__class__.__name__)
        self.set_thread_name(self.__class__.__name__)

        pass
    @property
    def wp(self):      
        if not self._wp:
            self._wp=WebPage()
        return self._wp

    @exception_decorator(error_state=False)
    def _handle_msg_imp(self, url,file_path):
        with self._logger.raii_target(url,file_path) as logger:
            logger.update_time(UpdateTimeType.STAGE)
            logger.trace("收到消息",update_time_type=UpdateTimeType.STAGE)
            listent_shop_api=[".m4a"]
            # self.wp.listen.stop()# 操作完成后释放资源
            self.wp.listen.start(listent_shop_api)
            if not self.wp.get(url):
                logger.error("失败",update_time_type=UpdateTimeType.STAGE)
                return
            #获取播放按钮，并单击
            play_button=self.wp.ele((By.XPATH,'//div[@class="play-btn U_s"]'),timeout=3)
            if not play_button:
                logger.error("失败",update_time_type=UpdateTimeType.STAGE)
                return
            play_button.click()
            
            packet = self.wp.listen.wait(timeout=60)
            if not packet:
                logger.error("失败",update_time_type=UpdateTimeType.STAGE)
                return
            body=packet.response.body

            write_to_bin(file_path,body)
            logger.error("成功",update_time_type=UpdateTimeType.STAGE)

    def _handle_data(self, data:dict):
        url=data.get("url")
        dest_path=data.get("dest_path")
        self._handle_msg_imp(url,dest_path)


def msgs_from_xlsx(xlsx_path,sheet_name):
    dest_root=Path(r"E:\旭尧\有声读物")
    df:pd.DataFrame=pd.read_excel(xlsx_path,sheet_name=sheet_name)
    
    results=df.to_dict(orient="records")
    msgs=[]
    # for index,row in df.iterrows():
    for row in reversed(results):
        url,album,name=row["href"],row["专辑名称"],row["name"]
        dest_dir=dest_root/album
        os.makedirs(dest_dir,exist_ok=True)

        dest_path=str(dest_dir/f"{name}.m4a")

        if os.path.exists(dest_path):
            continue
        msg={"url":f"https://www.ximalaya.com{url}","dest_path":dest_path}
        msgs.append(msg)

    return msgs


def main(xlsx_path,sheet_name):
    
    
    url_queue=Queue()
    stop_envent=threading.Event()

    interact=InteractUrl(url_queue,stop_envent)
    logger=logger_helper("下载音频")
    
    #获取消息
    for index,msg in enumerate(msgs_from_xlsx(xlsx_path,sheet_name)):
        with logger.raii_target(detail=f"第{index+1:03}个") :
            url_queue.put(msg)
            logger.trace("加入下载队列",f"{msg}")
    
    interact.start()
    
    
    stop_envent.set()
    url_queue.join()
    interact.join()
    
    logger.info("完成",update_time_type=UpdateTimeType.ALL)
    pass


if __name__ == "__main__":
    main(r"E:\旭尧\有声读物\晓北姐姐讲故事.xlsx","audio")

    pass
    
    
    