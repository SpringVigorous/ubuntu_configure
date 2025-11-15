from DrissionPage import WebPage
import time
import re
import concurrent.futures

from base import  logger_helper,UpdateTimeType
from base.except_tools import except_stack
from base.com_decorator import exception_decorator
from base.state import ReturnState
from handle_comment import NoteCommentWriter

from handle_config import time_info,redbook_setting,web_listen,web_path,content_flag,note_type_map
from redbook_tools import *

from data import *
from enum import Enum
from pathlib import Path
from redbook_path import *


from base import set_attributes,get_attributes


interact_logger=logger_helper("交互次数","展示")
def check_interact():
    limit,count= time_info.check_limit()
    
    interact_logger.trace(count,update_time_type=UpdateTimeType.STEP)
    if limit:
        time.sleep(time_info.big_interval)


@exception_decorator()
def click_more_info(more_info,sleep_time=.1):
    if more_info:
        more_info.click()
    check_interact()
    if sleep_time>.01: 
        time.sleep(sleep_time)
        
    # comment_logger.trace("more-click", f"第{index}次", update_time_type=UpdateTimeType.STEP)

#点击 more 子进程
def handle_more(show_mores,comment_logger):
    if not show_mores:
        return

    #同步
    for index,more_info in enumerate(show_mores):
        click_more_info(more_info,time_info.get_interval(index+1) )
    return
        
    #多线程
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        
        # 使用 enumerate 获取索引和元素
        futures = [executor.submit(click_more_info, more_info,3.0*(index+1.0)/10.0) for index,more_info in enumerate(show_mores)]
        
        # 等待所有任务完成
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()  # 获取结果或处理异常
            except Exception as e:
                comment_logger.error("异常",except_stack(),update_time_type=UpdateTimeType.ALL)

def net_exception(title:str)->bool:
    
    """"
    安全限制：
    """
    
    # 定义关键词列表
    keywords = ["网络", "连接", "超时", "错误", "异常", "失败","安全","限制"]
    
    # 构建正则表达式模式
    pattern = "|".join(keywords)
    
    # 使用正则表达式搜索
    return re.search(pattern, title)

class ResultType(Enum):
    ONLY_NOTE = 1
    ONLY_COMMENT = 2
    BOTH = 3
    
    @property
    def is_only_note(self)->bool:
        return self==ResultType.ONLY_NOTE
    
    @property
    def is_only_comment(self)->bool:
        return self==ResultType.ONLY_COMMENT
    
    @property
    def is_both(self)->bool:
        return self==ResultType.BOTH
    
#统计调用多少次会发生异常
web_logger=logger_helper("webPage","调用次数")

class InteractBase():
    def __init__(self,note_queue,comment_queue,interact_logger, result_type:ResultType.ONLY_NOTE,next_id_func,sec_sort_fun:None):
        self.call_count=0
        self.wp=WebPage()
        url='https://www.xiaohongshu.com/'
        self.webPage.get(url)
        self.interact_logger=interact_logger
        self.note_queue=note_queue
        self.comment_queue=comment_queue
        self.result_type=result_type
        self._theme=""
        self.sec_sort_fun=sec_sort_fun
        self.next_id_func=next_id_func
        


    def close_note(self):
        self.webPage.wait.eles_loaded(web_path.close_path)
        close_flag=self.webPage.ele(web_path.close_path)
        if close_flag:
            try:
                close_flag.click()
                time.sleep(.5)
            except:
                self.show_except_stack()
                
    @property
    def webPage(self):
        self.call_count+=1
        # web_logger.trace(self.call_count,update_time_type=UpdateTimeType.STEP)
        return self.wp
    
    
                
    @property
    def theme(self)->str:
        return self._theme
    def set_theme(self,theme:str):
        self._theme=theme
    @property
    def title(self)->str:
        val=re.sub(content_flag.title_suffix_pattern,"",self.webPage.title)
        return val.split(content_flag.no_tilte_split)[0]

    def show_except_stack(self):
        self.interact_logger.error("异常",f"{self.webPage.title}\n{except_stack()}",update_time_type=UpdateTimeType.ALL)

    #第一步，需要调用这个
    @exception_decorator()
    def click_seach_theme(self,theme,note_type=note_type_map.all):

        self.interact_logger.update_target("采集主题",theme)
        self.interact_logger.reset_time()
        self.interact_logger.info("开始",update_time_type=UpdateTimeType.ALL)

        #搜索输入框
        if not self.webPage.wait.ele_displayed(web_path.search_input_path):
            return False
        search_input = self.webPage.ele(web_path.search_input_path)
        search_input.clear()
        search_input.input(f'{theme}\n')
        # time.sleep(.4)

        #搜索按钮
        if not self.webPage.wait.ele_displayed(web_path.search_button_path):
            return False
        seach_button=self.webPage.ele(web_path.search_button_path)
        if not seach_button:
            sys.exit(0)
        seach_button.click()

        #如果是综合，就不需要再次搜索了
        if note_type==note_type_map.all:
            return True

        
        type_button=self.webPage.ele(note_type)
        if type_button:
            type_button.click()
        self.webPage.ele(web_path.search_button_path).click() #再次搜索下
        return True
    
    def theme_urls_path(self,theme)->str:
        return os.path.join(self.theme_dir,f"{theme}_urls.json")
        
    def load_theme_urls(self,theme)->list[str]:
        urls_path=self.theme_urls_path(theme)
        if os.path.exists(urls_path):
            with open(urls_path,"r",encoding="utf-8-sig") as f:
                return json.load(f) 
    
    def save_theme_urls(self,theme,urls:list[str]):
        urls_path=Path(self.theme_urls_path(theme))
        lst=[]
        
        if urls_path.exists():
            lst=self.load_theme_urls(theme)
        lst.extend(urls)
        lst=list(set(lst)) #去重
        
        with open(urls_path,"w",encoding="utf-8-sig") as f:
            json.dump(lst,f,ensure_ascii=False,indent=4)  
        self.interact_logger.info("保存url",urls_path,update_time_type=UpdateTimeType.STEP)
            
    
    def theme_urls(self,theme,search_count):
        #测试部分——————————————————————————————————————————————————
        urls_path=os.path.join(self.theme_dir,f"{theme}_urls.json")
        if os.path.exists(urls_path):
            with open(urls_path,"r",encoding="utf-8-sig") as f:
                return json.load(f) 
        #测试部分——————————————————————————————————————————————————
        self.interact_logger.update_target("采集url",theme)
        self.interact_logger.reset_time()
        self.interact_logger.info("开始")
        hrefs=[]
        try:

            #搜索输入框
            if not self.webPage.wait.ele_displayed(web_path.search_input_path):
                return
            search_input = self.webPage.ele(web_path.search_input_path)
            search_input.clear()
            search_input.input(f'{theme}\n')
            # time.sleep(.4)

            #搜索按钮
            if not self.webPage.wait.ele_displayed(web_path.search_button_path):
                return
            seach_button=self.webPage.ele(web_path.search_button_path)
            if not seach_button:
                sys.exit(0)
            self.webPage.ele(web_path.search_button_path).click()


            
            type_button=self.webPage.ele(note_type_map.all)
            if type_button:
                type_button.click()
            self.webPage.ele(web_path.search_button_path).click() #再次搜索下
            time.sleep(.5)

            while len(hrefs)<search_count:
                secManager=SectionManager(self.webPage,self.fixed_pos)
                secManager.update()
                time.sleep(.5)
                for item in secManager.urls:
                    if item not in hrefs:
                        hrefs.append(item)
                sec=secManager.last
                sec.click()
                self.close_note()

        except Exception as e:
            self.show_except_stack()
            
        #测试部分——————————————————————————————————————————————————
        with open(urls_path,"w",encoding="utf-8-sig") as f:
            json.dump(hrefs,f,ensure_ascii=False)  
        #测试部分——————————————————————————————————————————————————
  
        return hrefs
    
    
    def handle_theme_imp(self,theme,pfunc,search_count):
        if not self.click_seach_theme(theme):
            return False
        
        hrefs=[]
        
        
        #每条最多10s,超时后就退出
        each_usage_time=10
        
        total_usage_time=search_count*each_usage_time
        try:
 
            time.sleep(.5)
            # self.webPage.listen.start(web_listen.listen_note) 
            #忽略 标题
            secManager=SectionManager(self.webPage,self.next_id_func,self.sec_sort_fun)
            secManager.update()
            while len(hrefs)<search_count and self.interact_logger.usage_time(UpdateTimeType.ALL)<total_usage_time:
                logger=logger_helper(theme,f"第{len(hrefs)+1}条")
                logger.trace(f"开始",update_time_type=UpdateTimeType.STAGE)
                sec_item=secManager.next(self.title)
                sec=sec_item.sec if sec_item else None
                if not sec :
                    #更新表格
                    # secManager.resume_cur()
                    # secManager.set_wp(self.webPage)
                    secManager.update()
                    continue
                time.sleep(.5)
                
                try:
                    if(self.webPage.wait.ele_displayed(sec,timeout=5)):
                        sec.click()
                        logger.trace(f"已点击",update_time_type=UpdateTimeType.STEP)
                        
                    else:
                        secManager.resume_cur()
                        secManager.update()
                        continue
                    # sec.click()
                except:
                    logger.trace(f"未找到对应元素","再试一次",update_time_type=UpdateTimeType.STEP)
                    
                    secManager.resume_cur()
                    secManager.update()
                    continue   
                
                
                
                body=None
                times=0
                #重试4次
            
                while times<4 or logger.usage_time(UpdateTimeType.STEP)<each_usage_time*3:
                    times+=1
                    self.webPage.listen.start(web_listen.listen_note) 
                    item=self.webPage.listen.wait(timeout=10)
                    if not (item and item.response and item.response.body):
                        continue
                    body=item.response.body

                    if item.target==web_listen.listen_note:
                        break
                if not body:
                    continue
                
                
                url=self.webPage.url
                body["my_link"]=url
                body["title"]=self.title
                
                logger.trace(f"第{len(hrefs)+1}条成功",self.title,update_time_type=UpdateTimeType.STAGE)
                
                body=JsonData(theme=self.theme,json_data=body)
                hrefs.append(url)
                
                pfunc(body)
                self.close_note()
                time.sleep(.5)

                
        
        except Exception as e:
            self.interact_logger.error("异常",f"一共获取{len(hrefs)}个笔记\n{except_stack()}",update_time_type=UpdateTimeType.ALL)
            pass
        finally:
            self.interact_logger.info("完成",f"一共获取{len(hrefs)}个笔记",update_time_type=UpdateTimeType.ALL)
            
            self.save_theme_urls(self.theme,hrefs)

            return hrefs
        
   
    def handle_comment_func(self,csvj_writer):
        def pfunc(body):
            note_id=""
            try:
                note_id=body[1]['data']['items'][0]['id']
            except:
                pass
            self.handle_comment(csvj_writer,note_id=note_id)
        return pfunc
    def handle_note_func(self):
        def pfunc(body):
            self.note_queue.put(body)    #整理到内部队列
        return pfunc
    #只提取评论
    def handle_theme_comment(self,theme,csvj_writer,search_count):
        return self.handle_theme_imp(theme,self.handle_comment_func(csvj_writer),search_count)
    #只提取内容
    def handle_theme_note(self,theme,csvj_writer,search_count):
        return self.handle_theme_imp(theme,self.handle_note_func(),search_count)

    def handle_theme(self,theme,csvj_writer,search_count):
        
        func_map={
            ResultType.ONLY_NOTE:self.handle_theme_note,
            ResultType.ONLY_COMMENT:self.handle_theme_comment,
            ResultType.BOTH:self.handle_theme_note_comment
        }
        
        func=func_map.get(self.result_type,None)
        if func:
            return func(theme,csvj_writer,search_count)
        else:
            return None
        
        
        
    #提取内容+评论
    def handle_theme_note_comment(self,theme,csvj_writer,search_count):
        def fun(body):
            self.handle_note_func()
            self.handle_comment_func(csvj_writer)
        return self.handle_theme_imp(theme,fun,search_count)
        
        

    def handle_comment_by_urls(self,urls,csvj_writer:NoteCommentWriter):
        
        self.interact_logger.update_target("采集评论—url")
        self.interact_logger.reset_time()
        self.interact_logger.info("开始")
        for url in urls:

            if not self.webPage.get(url,timeout=10):
                continue
                
                # return ReturnState.NETEXCEPT
                    

            if net_exception(self.webPage.title):
                self.interact_logger.info("异常",f"{self.title}\n{except_stack()}",update_time_type=UpdateTimeType.STEP)   
                return ReturnState.NETEXCEPT
            
            
            # self.interact_logger.update_start()
            # time.sleep(.3)
            result=ReturnState.from_state(self.handle_comment(csvj_writer))
            if result.is_netExcept:
                self.interact_logger.info("异常",f"{self.title}\n{except_stack()}",update_time_type=UpdateTimeType.STEP)  
                return result
        self.interact_logger.info("完成",update_time_type=UpdateTimeType.ALL)
        
    #从缓存文件中获取
    @exception_decorator()
    def handle_comment_from_cache(self,title,comment_logger):

        cache_path=comment_html_cache_path(redbook_setting.note_path, self.theme,title)
        comment_container_html=None
        if os.path.exists(cache_path):
            with open(cache_path,"r",encoding="utf-8-sig") as f:
                comment_container_html=f.read()
            
            
        if not comment_container_html:
            return None
        total,count=get_attributes(comment_container_html,"div",["total","count"],[0],class_='comments-container')
        result=comment_container_html if int(total)==int(count)  and int(total)>0 else None
        if result:
            comment_logger.trace("已存在",f"从缓存中获取:{cache_path}",update_time_type=UpdateTimeType.STEP)
        
        return result
    
    @exception_decorator()
    def handle_comment_from_web(self,title,comment_logger):
        time.sleep(1)
        container=self.webPage.ele(web_path.comments_container_path,timeout=time_info.common_interval)
        comments_total=0
        try:
            raw_total=container.ele('.total').text
            splits=raw_total.split()
            if len(splits)>1:
                comments_total=int( splits[1])
        except:
            #网络问题，提前退出
            if net_exception(title):
                comment_logger.error("异常",f"{self.title}\n{except_stack()}",update_time_type=UpdateTimeType.STEP)
                return ReturnState.NETEXCEPT
            
            
            pass

        comment_logger.info("开始",f"总共{comments_total}个",update_time_type=UpdateTimeType.ALL)
        if comments_total<1:
            comment_logger.info("结束",f"共计时长",update_time_type=UpdateTimeType.ALL)
            return
        
        scroll_count=0
        
    
        #网络问题，提前退出
        if net_exception(title):
            comment_logger.error("异常",f"{self.title}\n{except_stack()}",update_time_type=UpdateTimeType.STEP)
            return ReturnState.NETEXCEPT
        

        
        while not self.webPage.wait.ele_displayed(web_path.comment_end_path,timeout=time_info.common_interval):
            #滚动
            if not self.webPage.wait.ele_displayed(web_path.note_scroll_path,timeout=time_info.common_interval):
                break
            scroller= self.webPage.ele(web_path.note_scroll_path)
            scroller.scroll.to_bottom()

            scroll_count+=1
            sleep_time=time_info.get_interval(scroll_count) 
            time.sleep(sleep_time)
            comment_logger.trace("滚动到底",f"第{scroll_count}次,等待{sleep_time}秒",update_time_type=UpdateTimeType.STEP)
        
            check_interact()
            #网络问题，提前退出
            if net_exception(title):
                comment_logger.error("异常",f"{self.title}\n{except_stack()}",update_time_type=UpdateTimeType.All)
                return ReturnState.NETEXCEPT
            
        comment_logger.info("滚动到底",f"共{scroll_count}次",update_time_type=UpdateTimeType.STAGE)
               
        time.sleep(1)

        more_index=1

        while True:        
            #更多评论
            show_mores=self.webPage.eles(web_path.comment_more_path,timeout=.5)
            comment_logger.trace("show-more",f"第{more_index}次,共{len(show_mores)}个",update_time_type=UpdateTimeType.STEP)
            if not show_mores:
                break
            handle_more(show_mores,comment_logger)
            more_count=len(show_mores)
            
            comment_logger.trace("more-click",f"共{more_count}个,完成",update_time_type=UpdateTimeType.STAGE)
            more_index+=1

            time.sleep(time_info.small_interval)
    
            #网络问题，提前退出
            if net_exception(title):
                comment_logger.error("异常",f"{self.title}\n{except_stack()}",update_time_type=UpdateTimeType.All)
                return ReturnState.NETEXCEPT

    
        #网络问题，提前退出
        if net_exception(title):
            comment_logger.error("异常",f"{self.title}\n{except_stack()}",update_time_type=UpdateTimeType.All)
            return ReturnState.NETEXCEPT
        
            
        comment_container=self.webPage.ele(web_path.comments_container_path,timeout=1)
        if not comment_container:
            comment_logger.info("评论为空","直接退出",update_time_type=UpdateTimeType.ALL)
            time.sleep(time_info.big_interval)
            return
        
        comments=self.webPage.eles(web_path.comment_content_path,timeout=3)
        html=set_attributes(comment_container.html,"div",["total","count"],[comments_total,len(comments) if comments else 0],class_='comments-container')
        self.hanlde_comment_to_cache(title,html,comment_logger)

        return  html
   
   #缓存评论html
    def hanlde_comment_to_cache(self,title,comment_container_html,comment_logger):

        cache_path=comment_html_cache_path(redbook_setting.note_path, self.theme,title)
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path,"w",encoding="utf-8-sig") as f:
            f.write(comment_container_html)
        comment_logger.trace("写入缓存文件",cache_path,update_time_type=UpdateTimeType.STEP)    
   
   
   #针对已打开的笔记，进行评论采集
    @exception_decorator() 
    def handle_comment(self,csvj_writer:NoteCommentWriter,note_id:str=""):
        #处理评论
        title=self.title
        comment_logger=logger_helper("采集评论",title)
        #从缓存中获取
        comment_container_html=self.handle_comment_from_cache(title,comment_logger)
        if not comment_container_html:
            comment_container_html=self.handle_comment_from_web(title,comment_logger)
            if not comment_container_html :
                return
            elif isinstance(comment_container_html,ReturnState):
                return comment_container_html 
        
        comment_logger.info("完成",f"共计时长",update_time_type=UpdateTimeType.ALL)

        #发送到笔记处理队列，并发执行
        comment_data=CommentData(csvj_writer,self.theme,comment_container_html,note_id,title)
        self.comment_queue.put(comment_data)



if __name__ == '__main__':
    from base import worm_root

    data=None
    with open(worm_root/r"red_book\notes\祛湿url\祛湿url_urls.json","r",encoding="utf-8-sig") as f:
        data= json.load(f) 
    print(data)