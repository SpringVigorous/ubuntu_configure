


# 1. 标准库（按字母顺序排列，统一风格）
import os
import threading
import time
from pathlib import Path
from queue import Queue
from typing import Callable,Any

# 2. 第三方库（按字母顺序排列，区分不同库）
import pandas as pd
from DrissionPage import WebPage
from selenium.webdriver.common.by import By

# base 模块：拆分长导入（用括号包裹，无需反斜杠，PEP8 推荐）
from base import (
    backup_xlsx,
    df_empty,
    exception_decorator,
    fill_url,
    is_http_or_https,
    logger_helper,
    priority_read_excel_by_pandas,
    read_from_txt_utf8,
    ThreadTask,
    UpdateTimeType,
    write_to_bin,
    write_to_txt_utf8,
    singleton,
    postfix,
    TaskStatus,Success,Undownloaded,Incompleted,
    audio_root
)


# 3. 自定义库（按模块分组，拆分过长导入，避免通配符）
# cg 模块：明确导入所需函数（移除通配符 *，避免命名空间污染）
from cg.audio_kenel import *
from audio_manager import AudioManager

def web_status(web_content:str)->TaskStatus:
    
    if "无法访问" in web_content:
        return TaskStatus.UNDOWNLOADED.set_not_found
    if "开会员，免费听" in web_content:
        return TaskStatus.UNDOWNLOADED.set_charged
    
    return TaskStatus.SUCCESS
    


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
    downloaded=row[downloaded_id] == TaskStatus.SUCCESS.value
    if downloaded or os.path.exists(dest_file):
        return
    if not is_http_or_https(url):
        url=f"https://www.ximalaya.com{url}"
    
    msg={url_id:url,
         dest_path_id:dest_file,
         }
    return msg

@exception_decorator(error_state=False)
def row_path_to_msg(row:dict,xlsx_path:str,sheet_name:str)->dict:
    results=row_dict_to_msg(row)
    if not results: return
    msg={
         xlsx_path_id:xlsx_path,
         sheet_name_id:sheet_name,
         }
    msg.update(results)
    return msg


sound_play_xpath='//div[@class="play-btn U_s"]'
#<i class="xuicon xuicon-web_video_btn_play_big play-btn"></i>
video_play_xpath='//i[@class="xuicon xuicon-web_video_btn_play_big play-btn"]'

buy_vip_xpath='//div[@class="price-btn buy-vip-btn kn_"]'

# title_sound_xpath='//i[@class="xuicon xuicon-sound-n v-m"]'
title_sound_xpath='//span[@class="v-m p-l-5" and text()="声音"]'
# <span class="v-m p-l-5">专辑</span>
title_album_xpath='//span[@class="v-m p-l-5" and text()="专辑"]'
# <span style="cursor: pointer;">加载更多</span>
# load_more_xpath='//span[@style="cursor: pointer;"]'
load_more_xpath='//span[@style="cursor: pointer;" and text()="加载更多"]'


#<li class="page-next page-item N_t"><a class="page-link N_t" href="javascript:;"></a></li>
next_page_xpath='//li[@class="page-next page-item N_t"]'


#<input type="number" placeholder="请输入页码" step="1" min="1" max="9" class="control-input N_t" value="">
page_input_xpath='//input[@class="control-input N_t" and @placeholder="请输入页码"]'

#<button disabled="" type="submit" class="btn disabled N_t">跳转</button>
jump_button_xpath='//button[@class="btn disabled N_t" and text()="跳转"]'

#<li class="page-item N_t"><a href="javascript:;" class="page-link N_t"><span>44</span></a></li>
page_count_xpath='//li[@class="page-item N_t"][last()]//span/text()'


@singleton
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
    
    #是否有问题，状态信息
    @property
    def web_error(self)->tuple[bool,TaskStatus]:
        status:TaskStatus=web_status(self.wp.html)
        has_error=status.is_error or status.is_not_found or status.is_charged
        return (has_error,status)
    
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
    def url_title(self,url:str):
        with self._lock:
            if not self.wp.get(url):
                return 
            time.sleep(5)
            

            #等待标题改变
            self.wp.wait.title_change("个人主页",exclude=False,timeout=10)
            return self.title
        
    @exception_decorator(error_state=False)
    def _handle_audio_url(self, url,audio_path)->tuple[str,TaskStatus]:
        body=None
        self._msg_count+=1
        suffix=None
        with self._logger.raii_target(f"第{self._msg_count}个audio消息",f"{url}->{audio_path}") as logger:
            param_dict={url_id:url,dest_path_id:audio_path}
            # logger.update_time(UpdateTimeType.STAGE)
            logger.trace(f"收到新消息",update_time_type=UpdateTimeType.STAGE)
            listent_shop_api=[".m4a",".mp4"]
            
            fail_status:TaskStatus= TaskStatus.UNDOWNLOADED
            
            with self._lock:
                # self.wp.listen.stop()# 操作完成后释放资源
                self.wp.listen.start(listent_shop_api)
                if not self.wp.get(url):
                    logger.error("失败","url失败",update_time_type=UpdateTimeType.STAGE)
                    self._failed_lst.append(param_dict)
                    return fail_status.set_not_found,suffix
                error,status=self.web_error
                if error:
                    logger.error("失败",status,update_time_type=UpdateTimeType.STAGE)
                    return suffix,status
                
                
                #获取播放按钮，并单击
                play_button=self.wp.ele((By.XPATH,sound_play_xpath),timeout=3)
                if not play_button:
                    play_button=self.wp.ele((By.XPATH,video_play_xpath),timeout=3)
                if not play_button:
                    logger.error("失败","找不到播放按钮",update_time_type=UpdateTimeType.STAGE)
                    self._failed_lst.append(param_dict)
                    
                    #<div class="price-btn buy-vip-btn kn_">6元开会员，免费听</div>
                    buy_button=self.wp.ele((By.XPATH,buy_vip_xpath),timeout=3)
                    if buy_button:
                        self._buy_lst.append(param_dict)
                    
                    return suffix,fail_status.set_error
                play_button.click()
                
                packet = self.wp.listen.wait(timeout=40)
                if not packet:
                    logger.error("失败","获取不到.m4a信息",update_time_type=UpdateTimeType.STAGE)
                    self._failed_lst.append(param_dict)
                    return fail_status.set_error ,suffix
                response=packet.response
                body=response.body
                cur_url=response.url
                suffix=postfix(cur_url,".m4a") 
                audio_path=str(Path(audio_path).with_suffix(suffix))

            write_to_bin(audio_path,body)
            logger.info("成功",audio_path,update_time_type=UpdateTimeType.STAGE)
            return suffix,TaskStatus.SUCCESS

    @exception_decorator(error_state=False)
    def _handle_bozhu_url(self, url)->tuple[str,TaskStatus]: #html
        
        content=None
        self._msg_count+=1
        with self._lock:
            with self._logger.raii_target(f"收到博主声音消息",f"{url}") as logger:
                
                if not self.wp.get(url):
                    logger.error("失败","url失败",update_time_type=UpdateTimeType.STAGE)
                    return content,Undownloaded().set_error

                # logger.update_time(UpdateTimeType.STAGE)
                logger.trace(f"收到新消息",update_time_type=UpdateTimeType.STAGE)
                #<i class="xuicon xuicon-sound-n v-m"></i>
                sound_btn=self.wp.ele((By.XPATH,title_sound_xpath),timeout=3)
                if sound_btn:
                    sound_btn.click()
                    time.sleep(.5)
                
                

                scoll_time=0
                
                try:
                    while True:
                        
                        #缓存结果，避免失败后，导致数据丢失（至少还能返回上次结果）
                        content=self.wp.html
                        error,status=self.web_error
                        if error:
                            logger.error("失败",status,update_time_type=UpdateTimeType.STAGE)
                            return content,status
                        #<span style="cursor: pointer;">加载更多</span>
                        more_button=self.wp.ele((By.XPATH,load_more_xpath),timeout=5)
                        if not (more_button and more_button.text):
                            break
                        scoll_time+=1
                        
                        # 滚动到可见区域并点击
                        # self.wp.scroll.to_see(more_flag.parent)
                        self.wp.scroll.to_bottom()
                        logger.trace("滚动成功",f"第{scoll_time}次",update_time_type=UpdateTimeType.STEP)
                        more_button.click()
                        time.sleep(.5)


                except Exception as e:
                    logger.error("失败",f"滚动失败{e}",update_time_type=UpdateTimeType.STAGE)
                    
                    
                try:
                    content=self.wp.html
                except Exception as e:
                    logger.error("失败",f"获取html失败{e}",update_time_type=UpdateTimeType.STAGE)

                
        return content,Success()
    @exception_decorator(error_state=False)
    def _handle_album_url(self, url)->tuple[str,TaskStatus]: #html
        
        content=None
        with self._lock:
            self._msg_count+=1
            with self._logger.raii_target(f"收到博主专辑消息",f"{url}") as logger:
                
                if not self.wp.get(url):
                    logger.error("失败","url失败",update_time_type=UpdateTimeType.STAGE)
                    return content,Undownloaded().set_error


                # logger.update_time(UpdateTimeType.STAGE)
                logger.trace(f"收到新消息",update_time_type=UpdateTimeType.STAGE)
                #<i class="xuicon xuicon-album-p v-m"></i>
                sound_btn=self.wp.ele((By.XPATH,title_album_xpath),timeout=3)
                if sound_btn:
                    sound_btn.click()
                    time.sleep(.5)

                scoll_time=0
                try:
                    while True:
                        content=self.wp.html
                        
                        error,status=self.web_error
                        if error:
                            logger.error("失败",status,update_time_type=UpdateTimeType.STAGE)
                            return content,status

                        
                        
                        more_button=self.wp.ele((By.XPATH,load_more_xpath),timeout=5)
                        if not( more_button and more_button.text):
                            break
                        scoll_time+=1
                        
                        # 滚动到可见区域并点击
                        # self.wp.scroll.to_see(more_flag.parent)
                        self.wp.scroll.to_bottom()
                        logger.trace("滚动成功",f"第{scoll_time}次",update_time_type=UpdateTimeType.STEP)
                        more_button.click()
                        time.sleep(.5)

                        
                except Exception as e:
                    logger.error("失败",f"滚动失败{e}",update_time_type=UpdateTimeType.STAGE)
                    
                    
                try:
                    content=self.wp.html
                except Exception as e:
                    logger.error("失败",f"获取html失败{e}",update_time_type=UpdateTimeType.STAGE)

                
        return content,Success()
  
    
  
    @exception_decorator(error_state=False)
    def _handle_sound_from_album_url(self, url)->tuple[list[dict],TaskStatus]: #html
        results=[]
        self._msg_count+=1

        with self._lock:
            with self._logger.raii_target(f"收到专辑消息",f"{url}") as logger:
                
                if not self.wp.get(url):
                    logger.error("失败","url失败",update_time_type=UpdateTimeType.STAGE)
                    return 

                # logger.update_time(UpdateTimeType.STAGE)
                logger.trace(f"收到新消息",update_time_type=UpdateTimeType.STAGE)
                #<i class="xuicon xuicon-album-p v-m"></i>
                jump_time=0
                time.sleep(5)
                try:
                    while True:
                        error,status=self.web_error
                        if error:
                            logger.error("失败",status,update_time_type=UpdateTimeType.STAGE)
                            return  results,status
                        
                        
                        
                        if result:=sound_by_album_content(self.wp.html):
                            results.extend(result)
                            
                            
                        next_page_btn=self.wp.ele((By.XPATH,next_page_xpath),timeout=3)
                        if next_page_btn:
                            next_page_btn.click()
                            
                            jump_time+=1
                            logger.trace("翻页成功",f"第{jump_time}次",update_time_type=UpdateTimeType.STEP)
                            time.sleep(.5)
                        else:
                            break

                        
                except Exception as e:
                    logger.error("失败",f"滚动失败{e}",update_time_type=UpdateTimeType.STAGE)

        return results,Success()
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
        self.manager=AudioManager()
    
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
        xlsx_path=data.get(xlsx_path_id)
        sheet_name=data.get(sheet_name_id)
        
        
        
        os.makedirs(os.path.dirname(dest_path),exist_ok=True)
        
        self._msg_count+=1
        success=self._impl._handle_audio_url(url,dest_path)
        
        #更新状态
        if success:
            suffix,status=success
            self.manager.update_status_suffix(xlsx_path,sheet_name,url,status,suffix)
            self._success_count+=1
        else:
            pass
            # self.manager.update_status(xlsx_path,sheet_name,url,TaskStatus.UNDOWNLOADED)
            
        
        
    def _final_run_after(self):
        self._impl.close()
        self._logger.info("统计信息",f"成功{self._success_count}个,失败{self._msg_count-self._success_count}个")


class InteractHelper():
    def __init__(self,logger:logger_helper,
                 interact_content_fun:Callable[[str],tuple[str,TaskStatus]]=None,
                 interact_df_func:Callable[[str],tuple[list[dict],TaskStatus]]=None,
                 content_convert_func:Callable[[str],tuple[list[dict],TaskStatus]]=None,
                 df_latter_func:Callable[[pd.DataFrame],pd.DataFrame]=None,
                 handle_row_func:Callable[[pd.Series],Any]=None
                 ) -> None:
        self.logger:logger_helper=logger
        
        self.set_interact_content_fun(interact_content_fun)
        self.set_content_convert_func(content_convert_func)
        self.set_df_latter_func(df_latter_func)
        self.set_handle_row_func(handle_row_func)
        self.set_interact_df_func(interact_df_func)
        
        self.manager=AudioManager()
        
    #df,TaskStatus
    @exception_decorator(error_state=False)
    def fetch_df(self,xlsx_path,sheet_name,url,html_path)->tuple[pd.DataFrame,TaskStatus]:
        df= self.manager.get_df(xlsx_path,sheet_name=sheet_name)
        if not df_empty(df):
            self.logger.info("忽略交互",f"直接从{xlsx_path}读取,sheetname={sheet_name}")
            return df,TaskStatus.SUCCESS
        
        if self.interact_df_func:
            if result:=self.interact_df_func(url):
                lst,status=result
                if not lst:
                    return df,status
                df=pd.DataFrame(self.interact_df_func(url))
            else:
                return df,Undownloaded().set_error
        else:
            result=self._fetch_url_content(url,html_path)
            if not result:
                return None,Undownloaded().set_fetch_error
            content,status=result
            if not content:
                return None,status
            if not self.content_convert_func:
                return None,Undownloaded().set_convert_error
            df=pd.DataFrame(self.content_convert_func(content))
        if df_empty(df):
            return None,Undownloaded().set_convert_error
        try:
            if self.df_latter_func:
                df=self.df_latter_func(df)
            if df_empty(df):
                return None,Undownloaded().set_post_error
            if xlsx_path:=backup_xlsx(xlsx_path,df,sheet_name=sheet_name):
                self.logger.info("保存成功",f"{xlsx_path}")
        except Exception as e:
            self.logger.error("保存失败",f"{e}")
            
        return df,TaskStatus.SUCCESS
    def _fetch_url_content(self,url,html_path)->tuple[str,TaskStatus]:
        if content:=read_from_txt_utf8(html_path):
            self.logger.info("忽略交互",f"直接从{html_path}读取")
            return content,Success()
        
        if not self.interact_fun:
            return None,Undownloaded().set_fetch_error
        result=self.interact_fun(url)
        if not result:
            return None,Undownloaded().set_fetch_error
        
        content,status=self.interact_fun(url)
        if not content:
            return None,status
        
        if content:
            write_to_txt_utf8(html_path,content)
            self.logger.info("网页保存到本地",f"{html_path}")
        return content,Success()
    @exception_decorator(error_state=False)
    def handle_df(self, df:pd.DataFrame,output_queue:Queue)->int:
        if not self.handle_row_func or df_empty(df):
            return
        audio_index=0
        for _,row in df.iterrows():

            msg=self.handle_row_func(row)
            if (msg):
                output_queue.put(msg)    
                audio_index+=1
                self.logger.trace("加入下载队列",f"第{audio_index}个消息{msg}")
                
        return audio_index

    def set_interact_content_fun(self,interact_fun:Callable[[str],tuple[str,TaskStatus]]=None) -> None:
        self.interact_fun:Callable[[str],tuple[str,TaskStatus]]=interact_fun
        
        
    def set_content_convert_func(self,content_convert_func:Callable[[str],tuple[list[dict],TaskStatus]]=None) -> None:
        self.content_convert_func:Callable[[str],tuple[list[dict],TaskStatus]]=content_convert_func
        
    def set_df_latter_func(self,df_latter_func:Callable[[pd.DataFrame],pd.DataFrame]=None) -> None:
        self.df_latter_func:Callable[[pd.DataFrame],pd.DataFrame]=df_latter_func
        
        
    def set_handle_row_func(self,handle_row_func:Callable[[pd.Series],Any]=None) -> None:
        self.handle_row_func:Callable[[pd.Series],Any]=handle_row_func

    def set_interact_df_func(self,interact_df_func:Callable[[str],pd.DataFrame]=None) -> None:
        self.interact_df_func:Callable[[str],tuple[list[dict],TaskStatus]]=interact_df_func




class InteractBoZhu(ThreadTask):
    
    def __init__(self,input_queue,output_queue,stop_envent,out_stop_event) -> None:
        super().__init__(input_queue,output_queue=output_queue,stop_event=stop_envent,out_stop_event=out_stop_event)
        self._impl:InteractImp=InteractImp()

        self.set_thread_name(self.__class__.__name__)
        self._success_count=0
        self._msg_count=0
        self._logger.update_target(self.__class__.__name__,"交互获取博主所有音频地址")
        self._xlsx_lsts=[]
        self._helper=InteractHelper(self.logger,
                                    interact_content_fun=self._impl._handle_bozhu_url,
                                    content_convert_func=sound_lst_from_author_content,
                                    # df_latter_func=update_df,
                                    handle_row_func=row_dict_to_msg
                                    )
        

        
        

    @exception_decorator(error_state=False)
    def _handle_data(self, url:str):
        self._msg_count+=1
        with self.logger.raii_target(f"第{self._msg_count}个博主消息",f"{url}") as logger:
            title=self._impl.url_title(url)
            html_path=audio_root/f"{title}.html"
            xlsx_path=html_path.with_suffix(".xml")

            #博主所有的音频
            cur_dir=audio_root/title
            #赋值
            
            def df_latter(df:pd.DataFrame)->pd.DataFrame:
                return AudioManager.update_df_status(author_sound_df_latter(df))
            self._helper.set_df_latter_func(df_latter)
            
            df,status=self._helper.fetch_df(xlsx_path,audio_sheet_name,url,html_path)
            if not df_empty(df):
                self._success_count+=1
                self._xlsx_lsts.append(xlsx_path,audio_sheet_name)

            self._helper.handle_df(df,self.output_queue)

    def _final_run_after(self):
        # self._impl.close()
        self._logger.info("统计信息",f"成功{self._success_count}个,失败{self._msg_count-self._success_count}个")




    @exception_decorator(error_state=False)
    def _handle_data(self, url:str):
        self._msg_count+=1
        with self.logger.raii_target(f"第{self._msg_count}个博主消息",f"{url}") as logger:
            title=self._impl.url_title(url)
            html_path=audio_root/f"{title}.html"
            xlsx_path=html_path.with_suffix(".xlsx")
            cur_dir=audio_root/title
            
            df,status=self.fetch_df(xlsx_path,url,html_path,cur_dir)
            if df_empty(df):
                return
            self._success_count+=1
            self._handle_df(df)

    def _final_run_after(self):
        # self._impl.close()
        self._logger.info("统计信息",f"成功{self._success_count}个,失败{self._msg_count-self._success_count}个")



class InteractAlbum(ThreadTask):
    
    def __init__(self,input_queue,output_queue,stop_envent,out_stop_event) -> None:
        super().__init__(input_queue,output_queue=output_queue,stop_event=stop_envent,out_stop_event=out_stop_event)
        self._impl:InteractImp=InteractImp()

        self.set_thread_name(self.__class__.__name__)
        self._success_count=0
        self._msg_count=0
        self._logger.update_target(self.__class__.__name__,"交互获取博主所有专辑地址")
        self._xlsx_lsts=[]
        self.manager=AudioManager()
        self._helper=InteractHelper(self.logger,
                                    interact_content_fun=self._impl._handle_album_url,
                                    content_convert_func=album_lst_from_content,
                                    # df_latter_func=self.manager.update_album_df,
                                    # handle_row_func=row_dict_to_msg
                                    )
        
        
    @exception_decorator(error_state=False)
    def _handle_data(self, url:str):
        df=None
        self._msg_count+=1
        with self.logger.raii_target(f"第{self._msg_count}个博主消息",f"{url}") as logger:
            title=self._impl.url_title(url)
            if not title:
                return
            
            
            
            html_path=audio_root/f"{title}_album.html"
            xlsx_path=html_path.with_suffix(".xlsx")
            cur_dir=audio_root/title
            def df_latter(df:pd.DataFrame)->pd.DataFrame:
                df[href_id]=df[href_id].apply(lambda x:fill_url(x,url))
                if not downloaded_id in df.columns:
                    df[downloaded_id]=TaskStatus.UNDOWNLOADED.value
                    
                def dest_path(title):
                    name= get_album_name(title)
                    return cur_dir/name/f"{name}_album.xlsx"
                    
                df[local_path_id]=df[title_id].apply(dest_path)
                
                return self.manager.update_album_df(df)
            self._helper.set_df_latter_func(df_latter)
            df,status=self._helper.fetch_df(xlsx_path,audio_sheet_name,url,html_path)
            
            #临时添加值
            # df=df_latter(df)
            # df.to_excel(xlsx_path,sheet_name=audio_sheet_name,index=False)
            
            if not df_empty(df):
                # self._xlsx_lsts.append((xlsx_path,audio_sheet_name))
                self._success_count+=1
                #缓存
                self.manager.cache_albumn_df(xlsx_path,audio_sheet_name,df)
            def row_to_msg(row:dict)->dict:
                if row[downloaded_id]==TaskStatus.SUCCESS.value:
                    return
                msg=row.to_dict()
                #当前博主所有的专辑，本地路径
                msg[cur_xlsx_path_id]=xlsx_path
                msg[cur_sheet_name_id]=audio_sheet_name
                return msg
            
            self._helper.set_handle_row_func(row_to_msg)
            self._helper.handle_df(df,self.output_queue)


        
    def _final_run_after(self):
        # self._impl.close()
        self._logger.info("统计信息",f"成功{self._success_count}个,失败{self._msg_count-self._success_count}个")
        
        
        
class InteractSoundFromAlbum(ThreadTask):
    def __init__(self,input_queue,output_queue,stop_envent,out_stop_event) -> None:
        super().__init__(input_queue,output_queue=output_queue,stop_event=stop_envent,out_stop_event=out_stop_event)
        self._impl:InteractImp=InteractImp()

        self.set_thread_name(self.__class__.__name__)
        self._success_count=0
        self._msg_count=0
        self._logger.update_target(self.__class__.__name__,"交互获取博主所有专辑地址")
        self._xlsx_lsts=[]
        self.manager=AudioManager()
        self._helper=InteractHelper(self.logger,
                                    interact_df_func=self._impl._handle_sound_from_album_url,
                                    # df_latter_func=AudioManager.update_df_status,
                                    handle_row_func=row_dict_to_msg
                                    )
        self._output_count:int=0
    @exception_decorator(error_state=False)
    def _handle_data(self, data:dict):
        url=data.get(href_id)
        album= get_album_name( data.get(title_id))
        xlsx_path=data.get(local_path_id)
        

        
        
        if not url or not xlsx_path:
            return
        cur_dir=Path(xlsx_path).parent
        html_path=""
        df=None
        self._msg_count+=1
        
        with self.logger.raii_target(f"第{self._msg_count}个专辑消息",f"{url}") as logger:
            
            def df_latter(df:pd.DataFrame)->pd.DataFrame:
                df.drop_duplicates(subset=[title_id,num_id],inplace=True)
                df[href_id]=df[href_id].apply(lambda x:fill_url(x,url))
                total=len(df)

                df[name_id]=df.apply(
                    lambda row:dest_title_name(
                        row[num_id],
                        row[title_id],
                        total
                        ),
                    axis=1
                    )
                df[local_path_id]=df[name_id].apply(lambda x:str(cur_dir/f"{x}.m4a"))
                df[album_name_id]=album
                return AudioManager.update_df_status(df)
            self._helper.set_df_latter_func(df_latter)
            df,status=self._helper.fetch_df(xlsx_path,audio_sheet_name,url,html_path)

            #更新状态
            if status.has_reaseon:
                pre_xlsx_path=data.get(cur_xlsx_path_id)
                pre_sheet_name=data.get(cur_sheet_name_id)
                self.manager.update_status(pre_xlsx_path,pre_sheet_name,url,status)
            
            
            
            
            if not df_empty(df):
                # self._xlsx_lsts.append((xlsx_path,audio_sheet_name))
                #缓存
                self.manager.cache_audio_df(xlsx_path,audio_sheet_name,df)
                
                self._success_count+=1
            else:
                pass
            

            self._helper.set_handle_row_func(lambda x: row_path_to_msg(x,xlsx_path,audio_sheet_name))
            self._output_count+=self._helper.handle_df(df,self.output_queue)
            
        #不要搞得太多，只处理这么多
        if self._output_count>200:
            self.clear_input()
            
            

    def _final_run_after(self):
        # self._impl.close()
        self._logger.info("统计信息",f"成功{self._success_count}个,失败{self._msg_count-self._success_count}个")