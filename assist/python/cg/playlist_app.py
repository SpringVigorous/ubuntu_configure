import sys
from queue import Queue
import threading

from pathlib import Path
import os




from base import ThreadTask,get_param_from_url,logger_helper,UpdateTimeType,exception_decorator,except_stack,df_empty,spceial_suffix_files,envent_sequence

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
            logger.trace(f"消息入队",f"第{index+1}条：\n【{url}】",update_time_type=UpdateTimeType.STEP)

    
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
        # VideoUrlInfo(url="https://www.laihuashow.com/hot/972606.html"),
        ]

   
    m3u8_urls=[


VideoUrlInfo(m3u8_url='https://pcvideoydott.titan.mgtv.com/c1/2025/05/14_0/228FAA06FA3BFED44798421AA486E01B_20250514_1_1_793_mp4/438D0380E470114011645FB00E2A138A.m3u8?arange=0&pm=temJU5Mzk25XffhwMqz3lwnmOcCxyHEQIRkzFB~bR~3rVw~BAi6sOvNLweSBNzk95W5k~Fw4qynyICbeeKbKtN0yCUBS3PFMGDM8eIN9Z6VCE0cbeOXkAsOH_kLVnBqFPISKG1TMnurAES_jlyft82qeJf2H~kJYJ1j6MLp_ov3S6oUQsLCoDz706YFzOMvPilOQXDuAGkrUHE2hFXatLwAo_21RRjvx5kROPJLIrenRCIy8zJH_YJS9Cw2bpWg4wbOacU~6~ompHENz5sv1TnmK6w42hK8icsNGmNIiHbL5G3KiyYgP7TGHkZPSALTG9kBiwQ9rqZB7Q~SpoWPpkpLpAPhFiVl99_tRJUB6znI573Ifnb_oJgb5gjNXuC_wJtP4wb0VcF33Ba2WxbM3DxlN7O8_QbJW&mr=qtaAqu4Hsj7FJLWcIhvpez_mwlFBWVLfOZ7sRVgdUMEUJkkjkm8jCEsupjUlyZGicOkjkwxqTnw9kK_r9vnRm7V~f~gjBkJP95Mhzo5xAy9lJxE5UOiXPzUvzDefEP7Tmloffk45J8tj~0HwiYNF5bktHH48O30p4P7eIQiSRjh80w_0yz~N5U8j2RroyyIX3~D_FdcBKWsSgVxk09fR3ifxguZlp~FZnWzKVfOJD43Fet6X~VdaEyfdVTPqNVV7lAbdPaNtHc0zDE4c~~uQYJT3JL_NINFtzyQcGea_zrBFv23m8wC~fdtzy0yWAkE1JOyM423iTDa8nyqHbZH1DWodYYAKKrMvVJlY2XOsY5RiHRp1egJX3qN0uG~dLWKsNWuIhKXPDnOB0nYT3L6Zwp0pUTgxdFheuGiAIi0fbevipd1dj1xpS4wDPr81SupxYZvwDNptORqqrvC7mSvAsfFsZ1LPTJCo9eCH6_bX1i9WNrKMsnx6ZAlc5bZwuOOWJVhxxPe_3_jIFXMof3Jhn7irl_IhhqSf4kuPcyhQZyvNKkVDVaRXWTOxcY0mewGbyCPYvtgMxQZEXZeHr64FYMLI51OKdwZwjV74s3CxmDjjm0jcacouvy_q0SiX9m09B6U6r0B84MUmKOWVi7TiDw--&uid=null&term=4&def=2&vc=AVC&scid=25066&cpno=6i06rp&ruid=ae0260278a1e4bcd&sh=1&ftc=webO1&sftc=v6.7.92ds0_vtp1', title='宝宝巴士之奇妙汉字第二季 第1集 房子从天降'),

    ]

    # app.send_msg(m3u8_urls) #直接提供m3u8_url
    # app.send_msg(raw_urls) #原始url，交互获取m3u8_url

    app.continue_decode() # 继续解码,前提是确保编码未处理
    
    # app.continue_merge() # 继续合并,前提是 已删除 加入的片段
    
    
    # app.continue_handle_url() #继续交互

    # app.continue_download() #继续下载
    
    # app.stop_merge_event.set() #关闭合并功能，手动删除多余片段后，再开启
    
    # app.stop_interact_event.set() #手动添加停止事件，关门手动网页交互功能;也可以直接关闭网页，起到相同效果
    
    app.run()
    app.save_df()
    pass


if  __name__ == '__main__':
    main()