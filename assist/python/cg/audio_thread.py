from cg.audio_kenel import *
import pandas as pd

from DrissionPage import WebPage
from selenium.webdriver.common.by import By

from base import logger_helper,exception_decorator,write_to_bin,UpdateTimeType,ThreadTask,write_to_txt_utf8,read_from_txt_utf8,is_http_or_https,df_empty,backup_xlsx
from pathlib import Path
import os
from queue import Queue
import threading
import time
from cg.audio_kenel import get_album_lst_from_content

audio_root=Path(r"E:\旭尧\有声读物")


    
@exception_decorator(error_state=False)
def dest_path(dest_dir:Path,album:str,name:str)->str:
    if not dest_dir:
        pass
    dest_dir=dest_dir/album
    result=str(dest_dir/f"{name}.m4a")
    return result



@exception_decorator(error_state=False)
def row_dict_to_msg(row:dict)->dict:
    url,dest_file=row[href_id],row[local_path_id]
    downloaded=row.get(downloaded_id,-1) == 1
    if downloaded or os.path.exists(dest_file):
        return
    if not is_http_or_https(url):
        url=f"https://www.ximalaya.com{url}"
    
    msg={url_id:url,dest_path_id:dest_file}
    return msg

def update_df_local_path(df:pd.DataFrame,cur_dir:Path=None)->pd.DataFrame:
    if df_empty(df): 
        return df
    # 2. 修正列名拼写错误，判断是否存在目标列
    if local_path_id not in df.columns:
        # 可选：如果列不存在，可初始化（根据你的需求决定是否添加）
        df[local_path_id] = ""  # 初始化所有值为-1（后续会被更新）

    
    # 3. 核心逻辑：仅给 downloaded < 0 的行重新赋值，>=0 的行不变
    # 构建条件掩码（定位需要更新的行）
    mask = df[local_path_id] ==""

    
    if not mask.any():
        return df
    
    # 仅对掩码为 True 的行应用赋值（axis=1 表示按行处理）
    df.loc[mask, local_path_id] = df.loc[mask].apply(
        lambda row: dest_path(cur_dir, row[album_id], row[name_id]),
        axis=1
    )
    # 4. 返回更新后的 DataFrame（必须返回，否则外部无法获取结果）
    return df
def update_df(df:pd.DataFrame,cur_dir:Path=None):
    if df_empty(df): 
        return df
    df=update_df_local_path(df,cur_dir)
    df=update_df_downloaded(df)
    return df

def update_df_downloaded(df:pd.DataFrame)->pd.DataFrame:
    if df_empty(df): 
        return df
    # 2. 修正列名拼写错误，判断是否存在目标列
    if downloaded_id not in df.columns:
        # 可选：如果列不存在，可初始化（根据你的需求决定是否添加）
        df[downloaded_id] = -1  # 初始化所有值为-1（后续会被更新）
    
    # 3. 核心逻辑：仅给 downloaded < 0 的行重新赋值，>=0 的行不变
    # 构建条件掩码（定位需要更新的行）
    mask = df[downloaded_id] < 0
    if not mask.any():
        return df
    def update_flag(row):
        return 1 if  os.path.exists(row[local_path_id]) else -1
        
    
    # 仅对掩码为 True 的行应用赋值（axis=1 表示按行处理）
    df.loc[mask, downloaded_id] = df.loc[mask].apply( update_flag,
        axis=1
    )
    
    # 4. 返回更新后的 DataFrame（必须返回，否则外部无法获取结果）
    return df



class InteractImp():
    def __init__(self) -> None:
        self._wp:WebPage=None
        self._logger=logger_helper()
        self._lock=threading.Lock()
        self._msg_count:int=0
        self._failed_lst=[]
        self._buy_lst=[]
    @property
    def wp(self):      
        if not self._wp:
            self._wp=WebPage()
        return self._wp
    
    @property
    def title(self)->str:
        name=self.wp.title
        if not name: 
            return "未知网页标题"
        pattern=re.compile(r"(.+?)的个人主页")
        if match:=pattern.match(name):
            name= match.group(1)
        
        return name
    
    @exception_decorator(error_state=False)
    def _handle_audio_url(self, url,audio_path):
        body=None
        with self._lock:
            self._msg_count+=1
            with self._logger.raii_target(f"第{self._msg_count}个audio消息",f"{url}->{audio_path}") as logger:
                param_dict={url_id:url,dest_path_id:audio_path}
                # logger.update_time(UpdateTimeType.STAGE)
                logger.trace(f"收到新消息",update_time_type=UpdateTimeType.STAGE)
                listent_shop_api=[".m4a"]
                # self.wp.listen.stop()# 操作完成后释放资源
                self.wp.listen.start(listent_shop_api)
                if not self.wp.get(url):
                    logger.error("失败","url失败",update_time_type=UpdateTimeType.STAGE)
                    self._failed_lst.append(param_dict)
                    return
                #获取播放按钮，并单击
                play_button=self.wp.ele((By.XPATH,'//div[@class="play-btn U_s"]'),timeout=3)
                if not play_button:
                    logger.error("失败","找不到播放按钮",update_time_type=UpdateTimeType.STAGE)
                    self._failed_lst.append(param_dict)
                    
                    #<div class="price-btn buy-vip-btn kn_">6元开会员，免费听</div>
                    buy_button=self.wp.ele((By.XPATH,'//div[@class="price-btn buy-vip-btn kn_"]'),timeout=3)
                    if buy_button:
                        self._buy_lst.append(param_dict)
                    
                    return
                play_button.click()
                
                packet = self.wp.listen.wait(timeout=40)
                if not packet:
                    logger.error("失败","获取不到.m4a信息",update_time_type=UpdateTimeType.STAGE)
                    self._failed_lst.append(param_dict)
                    return
                body=packet.response.body

                write_to_bin(audio_path,body)
                logger.info("成功",update_time_type=UpdateTimeType.STAGE)
                return True

    @exception_decorator(error_state=False)
    def _handle_bozhu_url(self, url)->tuple: #html
        
        title,content=[None]*2
        with self._lock:
            self._msg_count+=1
            with self._logger.raii_target(f"收到博主消息",f"{url}") as logger:
                
                if not self.wp.get(url):
                    logger.error("失败","url失败",update_time_type=UpdateTimeType.STAGE)
                    return
                
                # logger.update_time(UpdateTimeType.STAGE)
                logger.trace(f"收到新消息",update_time_type=UpdateTimeType.STAGE)
                #<i class="xuicon xuicon-sound-n v-m"></i>
                sound_btn=self.wp.ele((By.XPATH,'//i[@class="xuicon xuicon-sound-n v-m"]'),timeout=3)
                if sound_btn:
                    sound_btn.click()
                    time.sleep(.5)
                
                
                #<span style="cursor: pointer;">加载更多</span>
                more_button=self.wp.ele((By.XPATH,'//span[@style="cursor: pointer;"]'),timeout=3)
                scoll_time=0
                
                try:
                    while more_button and more_button.text:
                        scoll_time+=1
                        
                        # 滚动到可见区域并点击
                        # self.wp.scroll.to_see(more_flag.parent)
                        self.wp.scroll.to_bottom()
                        logger.trace("滚动成功",f"第{scoll_time}次",update_time_type=UpdateTimeType.STEP)
                        more_button.click()
                        time.sleep(.5)
                        #再次赋值
                        more_button=self.wp.ele((By.XPATH,'//span[@style="cursor: pointer;"]'),timeout=10)
                        #缓存结果，避免失败后，导致数据丢失（至少还能返回上次结果）
                        title,content=self.title,self.wp.html
                except Exception as e:
                    logger.error("失败",f"滚动失败{e}",update_time_type=UpdateTimeType.STAGE)
                    
                    
                try:
                    title,content=self.title,self.wp.html
                except Exception as e:
                    logger.error("失败",f"获取html失败{e}",update_time_type=UpdateTimeType.STAGE)

                
        return title,content

            
    def close(self):
        with self._lock:
            if  self.wp:
                self.wp.close()


class InteractAudio(ThreadTask):
    
    def __init__(self,input_queue,stop_envent) -> None:
        super().__init__(input_queue,output_queue=None,stop_event=stop_envent,out_stop_event=None)
        self._impl:InteractImp=InteractImp()

        self.set_thread_name(self.__class__.__name__)
        self._success_count=0
        self._msg_count=0
        self._logger.update_target(self.__class__.__name__,"交互获取音频")
        pass
    
    @property
    def fail_param_lst(self):
        return self._impl._failed_lst
    
    @property
    def buy_param_lst(self):
        return self._impl._buy_lst
    
    @exception_decorator(error_state=False)
    def _handle_data(self, data:dict):
        url=data.get(url_id)
        dest_path=data.get(dest_path_id)
        os.makedirs(os.path.dirname(dest_path),exist_ok=True)
        
        self._msg_count+=1
        success=self._impl._handle_audio_url(url,dest_path)
        if success:
            self._success_count+=1

        
        
    def _final_run_after(self):
        self._impl.close()
        self._logger.info("统计信息",f"成功{self._success_count}个,失败{self._msg_count-self._success_count}个")


class InteractBoZhu(ThreadTask):
    
    def __init__(self,input_queue,output_queue,stop_envent,out_stop_event) -> None:
        super().__init__(input_queue,output_queue=output_queue,stop_event=stop_envent,out_stop_event=out_stop_event)
        self._impl:InteractImp=InteractImp()

        self.set_thread_name(self.__class__.__name__)
        self._success_count=0
        self._msg_count=0
        self._logger.update_target(self.__class__.__name__,"交互获取博主所有音频地址")
        self._xlsx_lsts=[]
        pass

    @exception_decorator(error_state=False)
    def _handle_data(self, url:str):
        with self.logger.raii_target(f"第{self._msg_count}个博主消息",f"{url}") as logger:
            title,content=self._impl._handle_bozhu_url(url)
            html_path=audio_root/f"{title}.html"
            write_to_txt_utf8(html_path,content)
            self.logger.info("网页保存到本地",f"{html_path}")
            #博主所有的音频
            cur_dir=audio_root/title
            df=get_album_lst_from_content(content)
            
            if not df_empty(df):
                try:
                    # df[downloaded_id]=df.apply(lambda row:downloaded_status(cur_dir,row[album_id],row[name_id]),axis=1)
                    
                    df=update_df(df,cur_dir)
                    xml_path=html_path.with_suffix(".xml")
                    sheet_name="audio"
                    if xml_path:=backup_xlsx(xml_path,df,sheet_name=sheet_name):
                        self.logger.info("保存成功",f"{xml_path}")
                        self._xlsx_lsts.append((xml_path,sheet_name))
                except Exception as e:
                    self.logger.error("保存失败",f"{e}")
                    
            #测试，提前退出
            # return
            audio_index=0
            # os.makedirs(cur_dir,exist_ok=True)
            df=update_df(df,cur_dir)
            for _,row in df.iterrows():
                
                if (msg:=row_dict_to_msg(row)):
                    self.output_queue.put(msg)    
                    audio_index+=1
                    self.logger.trace("加入下载队列",f"第{audio_index}个消息{msg}")
            


        
        
    def _final_run_after(self):
        # self._impl.close()
        self._logger.info("统计信息",f"成功{self._success_count}个,失败{self._msg_count-self._success_count}个")



    