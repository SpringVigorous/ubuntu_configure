import sys
from DrissionPage import WebPage
from pathlib import Path
import os
import time



from base import (
    ThreadTask,get_param_from_url,find_last_value_by_col_val,get_next_filepath,write_to_json_utf8_sig,RetryOperater,fatal_link_error,logger_helper,UpdateTimeType,
    download_sync,UrlChangeMonitor,recycle_bin,sanitize_filename,BrowserClosedMonitor,set_link_error,ThreadPool,
    write_to_txt_utf8_sig,df_empty,read_from_txt_utf8_sig
)
from base import random_sleep
from base.except_tools import except_stack
from base.com_decorator import exception_decorator
import threading
from playlist_tools import *
from playlist_config import *
from playlist_data import *
from playlist_manager import playlist_manager



class InteractImp():
    def __init__(self,output_queue,stop_event):
        self._lock=threading.Lock()
        self._wp:WebPage=None
        self._logger=logger_helper(self.__class__.__name__)
        self._msg_count:int=0
        self._retry_operater=RetryOperater(3)

        self.output_queue=output_queue
        self.url_watcher:UrlChangeMonitor=None
        self.url_changed=False
        self.manager:playlist_manager=playlist_manager()
        self.stop_event=stop_event

        self.web_closed_watcher:BrowserClosedMonitor=None
        self.web_closed:bool=False
    def stop_watch(self):
        self.url_watcher.stop()
        self.web_closed_watcher.stop()
        
    @property
    def wp(self):
        
        
        if not self._wp:
            self._wp=WebPage()
            # self._wp.get("https://www.baidu.com")
            def _url_change(old, new):
                self.url_changed= old!=new
                if self.url_changed:
                    self._logger.trace(f"URL变化: {old} -> {new}")            # url='https://www.taobao.com/'
                    
            
                    
            self.url_watcher=UrlChangeMonitor(self.wp)
            self.url_watcher.add_callback(_url_change)
            self.url_watcher.start()
            
            
            self.web_closed_watcher:BrowserClosedMonitor=BrowserClosedMonitor(self.wp)
            def _web_closed():
                self._logger.trace(f"浏览器已关闭")      
                self.stop_watch()
                self.stop_event.set()
                self.web_closed=True
                #链接错误
                set_link_error(True)
                
            self.web_closed_watcher.add_callback(_web_closed)
            self.web_closed_watcher.start()
            
            #登录
            pass
        return self._wp
    @property
    def msg_count(self)->int:
        self._msg_count+=1
        return self._msg_count
    @property
    def fatal_error(self)->bool:
        return self._retry_operater.fatal_error or fatal_link_error()
    
    
    def clear_stop(self):
        self.stop_event.clear()
    
    @exception_decorator(error_state=False)
    def close(self):
        with self._lock:
            if not self._wp:
                return
            try:
                self.stop_watch()
                self._wp.close()
            except Exception as e:
                self._logger.trace("异常",except_stack())
                self._wp=None
            # self._wp=None

    def handle_loop(self):
        while not (self.stop_event.is_set() or self.web_closed):
            result=self.handle_imp()
            if not result:
                continue
            self.output_queue.put(result)
 

    @exception_decorator(error_state=False)
    def handle_url(self, info:VideoUrlInfo):
        if not info.has_m3u8_url:  # 不存在m3u8_url
            return self.handle_imp(info)
        else:
            return self.cache_url(info)


        
    @exception_decorator(error_state=False)   
    def cache_url(self, info:VideoUrlInfo)->list[dict]:
        logger=self._logger
        logger.update_target(f"收到第{self.msg_count}个消息:{info}")
        logger.info("成功")
        
        org_df=pd.DataFrame([info.to_dict])
        df=self.manager.update_video_df(org_df)
        if df_empty(df):
            df=org_df
        if df_empty(df):
            return
        return df.to_dict(orient="records")
        


    @exception_decorator(error_state=False)
    def handle_imp(self, url:str=None)->list[dict]:

        logger=self._logger
        has_url=bool(url)
        
        
        log_detail=f"收到第{self.msg_count}个消息:{url}" if  has_url else "监听url变化"
        if not has_url:
            try:
                url=self.wp.url
            except:
                return
        
        
        
        logger.update_target(log_detail,"监听事件")
        def do_func():
            # 捕获API数据包
            packet = self.wp.listen.wait(timeout=5)
            return packet

        
        def failure_func():
            self.wp.listen.stop()# 操作完成后释放资源
            logger.warn("未捕获到数据包，尝试重新监听...",update_time_type=UpdateTimeType.STEP)
            self.wp.listen.start(listent_shop_api)  # 重新启动监听
            self.wp.refresh()
            self.wp._wait_loaded()
        with self._lock:
            # 初始化监听
            # self.wp.listen.stop()# 操作完成后释放资源
            
            self._retry_operater.reset(2, normal_func=do_func, failure_func=failure_func)
            self.wp.listen.start(listent_shop_api)
            if has_url:
                self.wp.get(url)

            # 如果没有更新，则等待
            if self.wp.url in self.manager.urls:
                if has_url:
                    logger.info("url已存在，忽略此消息")
                    return
                self.url_changed=False
                #等待，直到url更新
                while not self.url_changed:
                    if self.stop_event.is_set():
                        return
                    self.wp.wait(5)
                #重新初始化监听
                self.url_changed=False

            logger.update_target(f"{self.wp.url}")
            try:
                self.wp._wait_loaded()
                self.wp.wait(1)
                packet=self._retry_operater.success()
                if not packet:
                    return
                # m3u8_url="https://v.cdnlz19.com/20240327/24526_7e693554/2000k/hls/mixed.m3u8"
                cur_url=self.wp.url
                
                m3u8_url=packet.url
                
                logger.info("成功",f"m3u8_urls:{m3u8_url}")
                body=packet.response.body
                m3u8_data=body.decode("utf-8") if body else ""
                title=sanitize_filename(self.wp.title).replace("-","_")
                return self.cache_url(m3u8_url,title,raw_url=cur_url,m3u8_data=m3u8_data)

            except Exception as e:
                logger.error("异常",except_stack(),update_time_type=UpdateTimeType.STAGE)

    
class InteractUrl(ThreadTask):
    def __init__(self,input_queue,output_queue,stop_event,out_stop_event):
        super().__init__(input_queue,output_queue=output_queue,stop_event=stop_event,out_stop_event=out_stop_event)
        self.interact:InteractImp=InteractImp(output_queue,stop_event)
        self.set_thread_name(self.__class__.__name__)
    @exception_decorator()
    def _handle_data(self, data:VideoUrlInfo):
        #致命错误，退出
        if self.interact.fatal_error:
            self.logger.error("收到致命错误","退出交互")
            self.clear_input()
            self.stop()
            return
        #可能有多个
        if not data or  not isinstance(data,VideoUrlInfo) or  not data.valid:
            return

        
        
        return self.interact.handle_url(data)

    def _final_run_after(self):
        self.interact.clear_stop()
        self.interact.handle_loop()
        self.interact.close()

class HandleUrl(ThreadTask):
    def __init__(self,input_queue,output_queue,stop_event,out_stop_event):
        super().__init__(input_queue,stop_event=stop_event,output_queue=output_queue,out_stop_event=out_stop_event)
        self.set_thread_name(self.__class__.__name__)
        
    @exception_decorator(error_state=False)
    def _handle_data_imp(self, data:dict):
        if not data  or not isinstance(data,dict):
            return

        info=VideoUrlInfo.from_dict(data)
        
        m3u8_url,video_name=info.m3u8_url,info.title


        logger=self.logger
        logger.update_target(m3u8_url,video_name)
        logger.update_time(UpdateTimeType.STAGE)
        logger.trace("开始")
        result=info.url_data
        logger.trace("完成",update_time_type=UpdateTimeType.STAGE)
        if not result:
            return
        result=list(result)
        result.extend([video_name,m3u8_url])
        return result
    
    
    @exception_decorator()
    def _handle_data(self, data):
        if data  is None or not isinstance(data,list):
            return

        for  item in data:
            result=self._handle_data_imp(item)
            if result:
                self.output_queue.put(result)
        


class DownloadVideo(ThreadTask):
    def __init__(self,input_queue,output_queue,stop_event,out_stop_event):
        super().__init__(input_queue,stop_event=stop_event,output_queue=output_queue,out_stop_event=out_stop_event)
        self.set_thread_name(self.__class__.__name__)
        self.manager:playlist_manager=playlist_manager()
        self._pool:ThreadPool=None
        
    @property
    def pool(self):
        if not self._pool:
            self._pool=ThreadPool(root_thread_name=self.thread_name)
        return self._pool   
    def _final_run_after(self):
        self.pool.join()
        
        
    @exception_decorator()
    def _handle_data(self, data):
        
        
        def callback(result, error):
            if not  result:
                return
            self.output_queue.put(result)
        
        self.pool.submit(self._download,data,callback=callback)
        
        # return self._download(data)
    
    

        
    def _download(self,data):

        key,iv,info_list,total_len,video_name,m3u8_url=data
        logger=logger_helper("下载视频...",f"{video_name}")
        
        if self.manager.has_downloaded(video_name):
            logger.debug(f"已下载过{video_name}","忽略此下载项")
            return
        
        
        url_list=[get_real_url(urls[2],m3u8_url)  for urls in info_list]
        logger.debug(f"总时长:{total_len}s,共{len(url_list)}个",update_time_type=UpdateTimeType.STAGE)
        temp_hash_name=video_hash_name(video_name)


        
        temp_path_list=temp_video_paths(len(url_list),temp_video_dir(video_name),postfix(url_list[0]))
        logger.update_time(UpdateTimeType.STAGE)
        logger.debug("开始")
        result= process_playlist(url_list, temp_path_list, key, iv, root_path, video_name, temp_hash_name)
        if not result:
            return
        
        result=list(result)
        result.append(video_name)
        logger.debug("完成",update_time_type=UpdateTimeType.STAGE)
        return result
            


        
class MergeVideo(ThreadTask):
    def __init__(self,input_queue,stop_event):
        super().__init__(input_queue,stop_event=stop_event,output_queue=None,out_stop_event=None)
        class_name=self.__class__.__name__

        self.set_thread_name(class_name)

        self.logger.update_target("文字识别")
        self.manager:playlist_manager=playlist_manager()
    @exception_decorator()
    def _handle_data(self,data):
        if not data :
            return
        
        return self._merge_video(data)
        



    @exception_decorator(error_state=False)
    def _merge_video(self,data):
       
        lost_count,success_paths,video_name=data
        
        temp_hash_name=video_hash_name(video_name)
        temp_root_dir=temp_video_dir(video_name)
        temp_video_path=normal_path(os.path.join(temp_root_dir,f"{temp_hash_name}.mp4"))
        dest_video=normal_path(dest_video_path(video_name))
        logger=self.logger
        logger.update_target("合并视频",temp_video_path)
        logger.update_time(UpdateTimeType.STAGE)
        
        logger.debug("开始","合并",update_time_type=UpdateTimeType.STEP)
        merge_video(success_paths,temp_video_path)
        logger.debug("完成","合并",update_time_type=UpdateTimeType.STEP)
        logger.update_time(UpdateTimeType.STEP)
        logger.update_target("合并视频+清理",dest_video)
        
        move_file(temp_video_path,dest_video)
        
        if lost_count==0:
            recycle_bin(temp_root_dir)
            logger.debug("完成" ,update_time_type=UpdateTimeType.STAGE)
        else:
            logger.error("部分缺失",f"缺失{lost_count}个文件",update_time_type=UpdateTimeType.STAGE)
            
        self.manager.set_downloaded(video_name,1)
        return True