


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
import math
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
    TaskStatus,Success,Undownloaded,Incompleted,TempCanceled,FetchError,
    audio_root,
    sanitize_filename,
    convert_time_str_to_seconds,
    ThreadPool,
    download_sync,
    normal_path,
    unique,

)


# 3. 自定义库（按模块分组，拆分过长导入，避免通配符）
# cg 模块：明确导入所需函数（移除通配符 *，避免命名空间污染）
from audio_kenel import *
from audio_manager import AudioManager
from audio_message import *

    
import time

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
    cur_statas:TaskStatus=TaskStatus.from_value(row[downloaded_id])
    if not cur_statas.can_download or os.path.exists(dest_file):
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

# next_page_xpath='//li[@class="page-next page-item N_t"]'

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

        
    @property
    def has_closed(self):
        try:
            self.wp.html
            return False
        except:
            return True
    
    @property
    def wp(self):      
        if not self._wp:
            self._wp=WebPage()
        return self._wp
    
    #是否有问题，状态信息
    @property
    def web_error(self)->tuple[bool,TaskStatus]:
        status:TaskStatus=web_status(self.wp.html)
        return (status.has_reason,status)
    @property
    def web_error_ignore_charged(self)->tuple[bool,TaskStatus]:
        status:TaskStatus=web_status(self.wp.html)
        return (status.clear_charged.has_reason,status)
    @property
    def title(self)->str:
        name=self.wp.title
        if not name: 
            return "未知网页标题"
        pattern=re.compile(r"(.+?)的个人主页")
        if match:=pattern.match(name):
            name= match.group(1)
        
        return sanitize_filename(name)
    @exception_decorator(error_state=False)
    def url_title(self,url:str):
        
        if title:= AudioManager().author_name_from_catalog(url):
            return title

        
        with self._lock:
            if not self.wp.get(url):
                return 
            time.sleep(5)
            

            #等待标题改变
            self.wp.wait.title_change("个人主页",exclude=False,timeout=10)
            return self.title
    @exception_decorator(error_state=False)
    def author_info(self,url:str):
        if info:= AudioManager().author_info(url):
            return info



    @property
    def audio_info(self):
        
        wp=self.wp
        # 获取所有包含数据的span元素
        root_div=wp.ele((By.XPATH,'//div[@class="info  kn_"]'))
        if not root_div:
            return
        span =wp.ele((By.XPATH,'//div[contains(@class, "category kn")]//span'))
        if not span:
            return
        
        
        result = {}
        

        span_class = span.get('class', '')
        text_content = ''.join(span.itertext()).strip()
        
        # 匹配日期时间（包含时间格式的文本）
        if 'time' in span_class and ':' in text_content and '-' in text_content:
            result['datetime'] = text_content
        
        # 匹配时长（包含时间格式且较短的文本）
        elif 'count' in span_class and ':' in text_content and len(text_content) <= 8:
            result['duration'] = text_content
        
        # 匹配播放量（包含"万"字或数字的文本）
        elif 'count' in span_class and ('万' in text_content or any(char.isdigit() for char in text_content)):
            # 过滤掉纯图标的文本
            if not any(keyword in text_content for keyword in ['xuicon', 'kn_']):
                result['views'] = text_content.strip()
    
        return result
    
        
    
    @exception_decorator(error_state=False)
    def _handle_audio_url(self, url,audio_path)->tuple[str,TaskStatus,str,dict]:
        body=None
        self._msg_count+=1
        suffix=None
        
        media_url=""
        info={}
        with self._logger.raii_target(f"第{self._msg_count}个audio消息",f"{url} -> {audio_path}") as logger:
            param_dict={url_id:url,dest_path_id:audio_path}
            # logger.update_time(UpdateTimeType.STAGE)
            logger.trace(f"收到新消息",update_time_type=UpdateTimeType.STAGE)
            listent_shop_api=AudioManager.media_suffix()
            

            logger_detail_str:str=""
            with self._lock:
                # self.wp.listen.stop()# 操作完成后释放资源

                if not self.wp.get(url):
                    logger.error("失败","url失败",update_time_type=UpdateTimeType.STAGE)

                    return suffix,NotFound(),media_url,info
                info=extract_audio_info(self.wp.html)


                #监听
                self.wp.listen.start(listent_shop_api)
                #再次检查
                has_error,status=self.web_error
                if has_error:
                    logger.error("失败",status,update_time_type=UpdateTimeType.STAGE)
                    status=status if has_error else FetchError()
                    return suffix,status,media_url,info
                if not info:
                    info=extract_audio_info(self.wp.html)
                    
                #获取播放按钮，并单击
                play_button=self.wp.ele((By.XPATH,sound_play_xpath),timeout=5)
                
                if not play_button:
                    play_button=self.wp.ele((By.XPATH,video_play_xpath),timeout=2)
                if not play_button:
                    logger.error("失败","找不到播放按钮",update_time_type=UpdateTimeType.STAGE)
                    has_error,status=self.web_error
                    if has_error:
                        status=status if has_error else FetchError()
                    return suffix,status ,media_url,info

                play_button.click()

                
                audio_wait_time=20
                if info :
                    if duration:=info.get(duration_id):
                        seconds=  convert_time_str_to_seconds(duration)
                        audio_wait_time=min(2.5,max(1,math.ceil(seconds/300.0)))*audio_wait_time
                
                packet = self.wp.listen.wait(timeout=audio_wait_time)
                if not packet:
                    logger.error("失败","获取不到.m4a信息",update_time_type=UpdateTimeType.STAGE)
                    #试验网页内容
                    # open(audio_root/"123.html","w",encoding="utf-8").write(self.wp.html)
                    has_error,status=self.web_error
                    if not has_error:
                        status= FetchError()
                    return suffix,status ,media_url,info
                
                
                response=packet.response
                body=response.body
                media_url=response.url
                suffix=postfix(media_url,".m4a") 
                dest_path=Path(audio_path)
                    
                if body:
                    write_to_bin(audio_path,body)
                    if dest_path.suffix !=suffix:
                        audio_path=str(dest_path.with_suffix(suffix))
                        logger_detail_str=f"修改最终路径：\n{audio_path}\n"
                    logger.info("成功",logger_detail_str,update_time_type=UpdateTimeType.STAGE)
                else:
                    logger.error("失败",update_time_type=UpdateTimeType.STAGE)
        #获取时长、发布时间、点赞数
        
        # cur_info= self.audio_info
        
        status=TaskStatus.SUCCESS if body else Undownloaded()
        
        return suffix,status,media_url,info


    @exception_decorator(error_state=False)
    def _handle_author_url(self, url)->tuple[str,TaskStatus]: #html
        
        content=None
        with self._lock:
            self._msg_count+=1
            with self._logger.raii_target(f"收到博主专辑消息",f"{url}") as logger:
                
                if not self.wp.get(url):
                    logger.error("失败","url失败",update_time_type=UpdateTimeType.STAGE)
                    return content,Undownloaded().set_not_found


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
                        
                        error,status=self.web_error_ignore_charged
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
    def _handle_album_url(self, url)->tuple[list[dict],TaskStatus]: #html
        results=[]
        self._msg_count+=1
        has_index:bool=True
        with self._lock:
            with self._logger.raii_target(f"收到专辑消息",f"{url}") as logger:
                
                if not self.wp.get(url):
                    logger.error("失败","url失败",update_time_type=UpdateTimeType.STAGE)
                    return result,Undownloaded().set_error

                # logger.update_time(UpdateTimeType.STAGE)
                logger.trace(f"收到新消息",update_time_type=UpdateTimeType.STAGE)
                #<i class="xuicon xuicon-album-p v-m"></i>
                jump_time=0
                time.sleep(5)
                try:
                    while True:
                        error,status=self.web_error_ignore_charged
                        if error:
                            logger.error("失败",status,update_time_type=UpdateTimeType.STAGE)
                            return  results,status
                        
                        
                        
                        has_index,result=sound_by_album_content(self.wp.html)
                        if result:   
                            # href_lst=list(map(lambda x:x[href_id],results))
                            # for item in result:
                            #     if item[href_id] in href_lst:
                            #         continue
                            #     results.append(item)
                                                 
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
                    
        #去重
        results=unique(results,lambda x:x[href_id])
        
        #重新编号
        if not has_index:
            for index,result in enumerate(results):
                result[num_id]=index+1
        
        return results,Success() if results else FetchError()
    def close(self):
        with self._lock:
            try:
                if  self.wp:
                    self.wp.close()
            except:
                pass


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
        
        
        self._charged_dir=[]

    def contains_charged(self,audio_path:str):
        cur_dir=normal_path(str(Path(audio_path).parent))
        return cur_dir in self._charged_dir

        
    def add_charged(self,audio_path:str):
        cur_dir=normal_path(str(Path(audio_path).parent))
        if cur_dir not in self._charged_dir:
            self._charged_dir.append(cur_dir)

    """
    data:dict={
        url_id:str,
        dest_path_id:str,
        xlsx_path_id:str,
        sheet_name_id:str
    }

    """
    @exception_decorator(error_state=False)
    def _handle_data(self, data:dict):
        if self._impl.has_closed :
        # if self._impl.has_closed:
            self.clear_input()
            return
        if self._msg_count>0 and self._msg_count % 210==0:
            time.sleep(120)
            
        
        url=data.get(url_id)
        dest_path=data.get(dest_path_id)
        xlsx_path=data.get(xlsx_path_id)
        sheet_name=data.get(sheet_name_id)
        
        #已存在就忽略
        if dest_path and os.path.exists(dest_path):
            return
        
        
        
        #遇到收费的，提前结束
        if self.contains_charged(dest_path):
            msg=AlbumUpdateMsg(xlsx_path,sheet_name,url,Charged())
            self.manager.update_album_df(msg)
            return
        
        self._msg_count+=1
        os.makedirs(os.path.dirname(dest_path),exist_ok=True)
        #更新状态
        if success:=self._impl._handle_audio_url(url,dest_path):
            suffix,status,media_url,info=success
            
            #记录收费的专辑
            if status.is_charged:
                self.add_charged(dest_path)
            
            
            if not info:
                info={}
            info.update({
                href_id:url,
                downloaded_id:status,
                suffix_id:suffix,
                media_url_id:media_url
            })
            
            
            msg=AlbumUpdateMsg(xlsx_path,sheet_name,url,status,suffix,info.get(duration_id),info.get(release_time_id),info.get(view_count_id),media_url)
            
            self.manager.update_album_df(msg)

            #判断是否成功
            if media_url:
                self._success_count+=1
        else:
            pass

            
        
    
    @exception_decorator(error_state=False)
    def _final_run_after(self):

        self._impl.close()
        
        logger_infos=[f"成功{self._success_count}个,失败{self._msg_count-self._success_count}个"]
        if self._charged_dir:
            logger_infos.append(f'收费的文件夹如下：\n{"\n".join(self._charged_dir)}')
        
        self._logger.info("统计信息",f"\n{','.join(logger_infos)}\n",update_time_type=UpdateTimeType.ALL)

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
    @exception_decorator(error_state=False,error_return=(None,Undownloaded().set_error))
    def fetch_df(self, xlsx_path, sheet_name, url, html_path) -> tuple[pd.DataFrame, TaskStatus]:
        # 尝试从缓存读取
        df = self.manager.get_df(xlsx_path, sheet_name=sheet_name)
        if not df_empty(df):
            self.logger.trace("忽略交互", f"直接从{xlsx_path}读取,sheetname={sheet_name}")
            return df, TaskStatus.SUCCESS

        # 获取数据
        if self.interact_df_func:
            interact_result = self.interact_df_func(url)
            if not interact_result :
                self.logger.error("失败", f"self.interact_df_func()异常")
                return df, Undownloaded().set_error
            lst, status = interact_result
            if not lst:
                self.logger.error("失败", f"self.interact_df_func()无结果")
                return df, status
            df = pd.DataFrame(lst)
        else:
            # 非交互模式：下载并转换内容
            fetch_result = self._fetch_url_content(url, html_path)
            if not fetch_result :
                self.logger.error("失败", f"self._fetch_url_content()异常")
                return None, Undownloaded().set_fetch_error
            content, status = fetch_result
            if not content:
                self.logger.error("失败", f"self._fetch_url_content()无结果")
                return None, status
            if not self.content_convert_func:
                self.logger.error("失败", f"self.content_convert_func 未赋值")
                return None, Undownloaded().set_convert_error
            convert_result = self.content_convert_func(content)
            if not convert_result:
                self.logger.error("失败", f"self.content_convert_func()异常")
                return None, Undownloaded().set_convert_error
            lst, status = convert_result
            if not lst:
                self.logger.error("失败", f"self.content_convert_func()无结果")
                return None, status
            df = pd.DataFrame(lst)

        # 验证数据
        if df_empty(df):
            return None, Undownloaded().set_convert_error

        # 后处理
        try:
            if self.df_latter_func:
                df = self.df_latter_func(df)
            if df_empty(df):
                self.logger.warn("失败", f"df为空")
                return None, Undownloaded().set_post_error
            
            


            if backup_xlsx(xlsx_path, df, sheet_name=sheet_name):
                self.logger.info("保存成功", f"{xlsx_path}")
        except Exception as e:
            self.logger.error("保存失败", f"{e}")

        return df, TaskStatus.SUCCESS
    @exception_decorator(error_state=False,error_return=(None,Undownloaded().set_error))
    def _fetch_url_content(self, url, html_path) -> tuple[str, TaskStatus]:
        # 尝试从缓存读取
        if content := read_from_txt_utf8(html_path):
            self.logger.info("忽略交互", f"直接从{html_path}读取")
            return content, Success()
        
        # 检查交互函数
        if not self.interact_fun:
            return None, Undownloaded().set_fetch_error
        
        # 获取内容
        result = self.interact_fun(url)
        if not result:
            return None, Undownloaded().set_fetch_error
        
        content, status = result
        if not content:
            return None, status
        
        # 保存内容
        write_to_txt_utf8(html_path, content)
        self.logger.info("网页保存到本地", f"{html_path}")
        return content, Success()
    @exception_decorator(error_state=False)
    def handle_df(self, df:pd.DataFrame,output_queue:Queue)->int:
        if not self.handle_row_func or df_empty(df):
            return
        self.logger.update_time(UpdateTimeType.STAGE)

        msg_lst=[]
        
        
        for _,row in df.iterrows():
            if row.empty:
                continue
            msg=self.handle_row_func(row)
            if not msg:
                continue
            msg_lst.append(msg)
        if not msg_lst:
            return len(msg_lst)    
        
        
        
        for index,msg in enumerate(msg_lst):
            output_queue.put(msg)    
            self.logger.trace("加入下载队列",f"第{index}个消息{msg}")
                
        msg_count=len(msg_lst)
        self.logger.info("发送消息成功",f"共{msg_count}个消息",update_time_type=UpdateTimeType.STAGE)
        return msg_count    


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
        self._logger.update_target(self.__class__.__name__,"交互获取博主所有专辑地址")
        self._xlsx_lsts=[]
        self.manager=AudioManager()
        self._helper=InteractHelper(self.logger,
                                    interact_content_fun=self._impl._handle_author_url,
                                    content_convert_func=album_lst_from_content,
                                    # df_latter_func=self.manager.update_album_df,
                                    # handle_row_func=row_dict_to_msg
                                    )
            
    @exception_decorator(error_state=False)
    def _cache_catalog(self,url,author,local_path:str,count=0)->dict:
        #缓存当前博主信息
        xlsx_path,sheet_name,catalog_df= self.manager.catalog_df
        
        
        status=  TempCanceled()  if self.manager.ignore_album else TaskStatus.UNDOWNLOADED
        
        result= {
                    href_id:url,
                    author_id:author,
                    downloaded_id: status. value,
                    local_path_id:local_path,
                    album_count_id:count,
                    downloaded_count_id:0,
                }
        result.update(get_create_modify_dict())
        catalog_result=[result]
        
        cur_df=pd.DataFrame(catalog_result)
        
        if df_empty(catalog_df):
            self.manager.cache_catalog_df(xlsx_path, sheet_name, pd.DataFrame(catalog_result))
        else:
            
            result_df,cut_df= self.manager.update_df(catalog_df,cur_df,keys=[href_id])
            if not df_empty(result_df): 
                self.manager.cache_catalog_df(xlsx_path, sheet_name, result_df)

        return self._impl.author_info(url)
            
    @exception_decorator(error_state=False)
    def _handle_data(self, url: str):
        if self._impl.has_closed:
            self.clear_input()
            return
        
        df = None
        self._msg_count += 1
        with self.logger.raii_target(f"第{self._msg_count}个博主消息", f"{url}") as logger:
            info= self._impl.author_info(url)
            info_valid=bool(info)
            if not info_valid:
                author_name = self._impl.url_title(url)
            else:
                author_name = info.get(author_id)
            
            
            # 1. 使用提前返回处理边界情况
            if not author_name:
                return
            
            xlsx_path,sheet_name = AudioManager.author_xlsx_info(author_name)
            #缓冲作者信息
            if not info_valid:
                self._cache_catalog(url, author_name,xlsx_path,0)

            html_path = AudioManager.author_html_path(author_name)
            def df_latter(df: pd.DataFrame) -> pd.DataFrame:
                df[href_id] = df[href_id].apply(lambda x: fill_url(x, url))
                # 2. 使用更Pythonic的 `not in` 语法
                if downloaded_id not in df.columns:
                    df[downloaded_id] = TaskStatus.UNDOWNLOADED.value

                df[album_id]=df[title_id].apply(get_album_name)
                def dest_path(title):
                    cur_path,_=AudioManager.album_xlsx_info(author_name,title)
                    
                    return cur_path

                df[local_path_id] =df.apply(lambda row: dest_path(row[album_id]),axis=1)

                return self.manager.update_summary_df(df)

            self._helper.set_df_latter_func(df_latter)
            df, status = self._helper.fetch_df(xlsx_path, sheet_name, url, html_path)

            
            # 3. 合并重复的条件判断：先统一处理DataFrame为空的情况并提前返回
            if df_empty(df):
                return

            #更新博主专辑数
            self.manager.update_author_album_count(url,df.shape[0])

            # 主流程：当df不为空时才执行以下操作
            self._success_count += 1
            self.manager.cache_author_df(xlsx_path, sheet_name, df)

            def row_to_msg(row: dict) -> dict:
                # 筛选消息
                status:TaskStatus=TaskStatus.from_value(row[downloaded_id])
                
                # if not status.can_download :
                #     return None
                if status.is_success:
                    return None
                
                
                msg = row.to_dict()
                msg[parent_xlsx_path_id] = xlsx_path
                msg[parent_sheet_name_id] = sheet_name
                msg[parent_url_id]=url
                
                #附加信息
                msg[author_id]=author_name
                
                # 专辑名
                msg[album_id]=get_album_name(row[title_id])
                
                return msg

            self._helper.set_handle_row_func(row_to_msg)

            # 处理需要下载的数据
            df = df[df[downloaded_id] < TaskStatus.SUCCESS.value]
            # df=df.reindex(index=df.index[::-1])
            self._helper.handle_df(df, self.output_queue)

        
    @exception_decorator(error_state=False)
    def _final_run_after(self):
        # self._impl.close()
        self._logger.info("统计信息",f"成功{self._success_count}个,失败{self._msg_count-self._success_count}个",update_time_type=UpdateTimeType.ALL)
        
        
        
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
                                    interact_df_func=self._impl._handle_album_url,
                                    # df_latter_func=AudioManager.update_df_status,
                                    handle_row_func=row_dict_to_msg
                                    )
        self._output_count:int=0
        
        """
        data:dict={           
            href_id:"",
            album_id:"",
            local_path_id:"",
            parent_xlsx_path_id:"",
            parent_sheet_name_id:"",
        }
        
        """
    @exception_decorator(error_state=False)
    def _handle_data(self, data:dict):
        if self._impl.has_closed:
            self.clear_input()
            return
        
        
        url=data.get(href_id)
        album_name= data.get(album_id) or get_album_name( data.get(title_id))
        xlsx_path=data.get(local_path_id)

        if not url or not xlsx_path:
            return
        
        xlsx_path=Path(xlsx_path)
        author_name=data.get(author_id)
        if not author_name:
            author_name=Path(xlsx_path).parent.stem
            pass
        html_path=""
        df=None
        self._msg_count+=1
        
        with self.logger.raii_target(f"第{self._msg_count}个专辑消息",f"{url}") as logger:
            @exception_decorator(error_state=False)
            def df_latter(df:pd.DataFrame)->pd.DataFrame:
                
                df.drop_duplicates(subset=[href_id],inplace=True)
                df.reset_index(drop=True, inplace=True)
                
                df[href_id]=df[href_id].apply(lambda x:fill_url(x,url))
                total=len(df)
                df[title_id]=df[title_id].apply(lambda x: sanitize_filename(x))
                df[name_id]=df.apply(
                    lambda row:dest_title_name(
                        row[num_id],
                        row[title_id],
                        total
                        ),
                    axis=1
                    )
                df[local_path_id]=df[name_id].apply(lambda x:str(AudioManager.file_path(file_name=f"{x}.m4a",author_name=author_name,album_name=album_name) ))
                df[album_name_id]=album_name
                df[view_count_id]=-1
                df[duration_id]=""

                
                
                # 强制忽略(只针对新增的)
                if self.manager.force_ignore_sound:
                    
                    mask=df[downloaded_id].apply(lambda x:TaskStatus.from_value(x).can_download)
                    for index,row in df[mask].iterrows():
                        df.loc[index,downloaded_id]=(TaskStatus.UNDOWNLOADED | TaskStatus.TEMP_CANCELED) .value
                    self.logger.info("强制忽略","忽略新增的音频消息")
                    
                return df

            self._helper.set_df_latter_func(df_latter)
            df,status=self._helper.fetch_df(xlsx_path,audio_sheet_name,url,html_path)
            
            #如果有收费的，则整个专辑添加收费标签
            if not df_empty(df) and any(df[downloaded_id].apply(lambda x:TaskStatus.from_value(x).is_charged)):
                if status.is_success:
                    status=Undownloaded()

                status=status.set_charged 
            #更新状态
            if status.has_reason :
                parent_xlsx_path=data.get(parent_xlsx_path_id)
                parent_sheet_name=data.get(parent_sheet_name_id)

                self.manager.update_status(parent_xlsx_path,parent_sheet_name,url,status)

            
            if not df_empty(df):
                # self._xlsx_lsts.append((xlsx_path,audio_sheet_name))
                #缓存
                self.manager.cache_album_df(xlsx_path,audio_sheet_name,df)
                
                self._success_count+=1
            else:
                pass
            
            # if self.manager.force_ignore_sound:
            #     self.logger.info("强制忽略","忽略所有音频消息")
            #     return

            self._helper.set_handle_row_func(lambda x: row_path_to_msg(x,xlsx_path,audio_sheet_name))
            filter_df=self.manager.filter_can_download_df(df)
            if result:=self._helper.handle_df(filter_df,self.output_queue):
            
                self._output_count+=result
            

            
            

    @exception_decorator(error_state=False)
    def _final_run_after(self):
        # self._impl.close()
        self._logger.info("统计信息",f"成功{self._success_count}个,失败{self._msg_count-self._success_count}个",update_time_type=UpdateTimeType.ALL)
        
        
        
class DownloadVideo(ThreadTask):
    def __init__(self,input_queue,stop_event):
        super().__init__(input_queue,stop_event=stop_event,output_queue=None,out_stop_event=None)
        self.set_thread_name(self.__class__.__name__)
        self._pool:ThreadPool=None
        self.logger.update_target("音频下载",self.__class__.__name__)
        self._msg_count:int=0
    @property
    def pool(self):
        if not self._pool:
            self._pool=ThreadPool(root_thread_name=self.thread_name)
        return self._pool   
    @exception_decorator(error_state=False)
    def _final_run_after(self):
        self.pool.join()
        self.logger.info("完成",f"下载{self._msg_count}个音频消息",update_time_type=UpdateTimeType.ALL)
        
    @exception_decorator(error_state=False)
    def _handle_data(self, data:list[tuple[str,str]]):

        self.logger.update_time(UpdateTimeType.STAGE)

        self.pool.submit(self._download,data)

    def _download(self,data):
        
        headers = {
                    'Accept': '*/*',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Connection': 'keep-alive',
                    'Range': 'bytes=0-',
                    'Referer': 'https://www.ximalaya.com/',
                    'Sec-Fetch-Dest': 'audio',
                    'Sec-Fetch-Mode': 'no-cors',
                    'Sec-Fetch-Site': 'cross-site',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.97 Safari/537.36 SE 2.X MetaSr 1.0',
                    'sec-ch-ua': '"Not)A;Brand";v="24", "Chromium";v="116"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                }
        
        for index,(url,audio_path) in enumerate(data):
            self._msg_count+=1
            with self.logger.raii_target(detail=f"第{index+1}个消息：{url}->{audio_path}") as logger:
                if os.path.exists(audio_path):
                    self.logger.info("跳过",f"音频文件已存在：{audio_path}")
                    continue
                sucess=download_sync(url,audio_path,headers=headers)
                if sucess:
                    logger.trace("下载成功",update_time_type=UpdateTimeType.STAGE)
                else:
                    logger.error("下载失败",update_time_type=UpdateTimeType.STAGE)
        

            

